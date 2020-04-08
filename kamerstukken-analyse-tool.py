# Web page scraping
from lxml import html
import requests

# XML parser
import xml.etree.ElementTree as ET

import csv

from kamerstuk import Kamerstuk
kamerstukken = {}

import nltk
from nltk.corpus import stopwords

def retrieveXML(kamerstuk):
	retrievedKS = Kamerstuk()
	# Pretend we are a google bot to avoid cookie popups https://support.google.com/webmasters/answer/1061943
	headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36'}

	# Retrieve kamerstuk
	kamerstukRequest = requests.get(kamerstuk.link, headers=headers)

	if kamerstukRequest.status_code == 200:
		retrievedKS = parseXML(kamerstuk, kamerstukRequest.content)
	else:
		raise Exception("Kamerstuk niet kunnen ophalen: "+kamerstuk.link)

	return retrievedKS

def parseXML(kamerstuk, rawText):
	global kamerstukken

	# Start with the root element
	root = ET.fromstring(rawText)

	# Metadata
	kamerstuk.kamer = root.find('kamerstuk/stuk/stuknr/ondernummer').attrib['kamer']
	dossiernr = root.find('kamerstuk/dossier/dossiernummer/dossiernr').text.replace(" ", "")
	stuknr = root.find('kamerstuk/stuk/stuknr/ondernummer').text
	kamerstuk.nummer = 'kst-'+dossiernr+'-'+stuknr
	kamerstuk.titel = root.find('kamerstuk/stuk/titel').text
	
	kamerstuk.freqTerms = findImportantTerms(str(rawText))

	#kamerstuk references
	kamerstuk.refs = []
	for kamerstukRef in root.iter('extref'):
		if "kst-" in kamerstukRef.attrib["doc"]:
			kamerstuk.refs.append(kamerstukRef.attrib["doc"])

	#set into global kamerstukken
	kamerstukken[kamerstuk.nummer] = kamerstuk

	print(kamerstuk.nummer+' - '+kamerstuk.titel)
	return kamerstuk

def findImportantTerms(text):
	cleanText = NLTKremoveStopwords(nltk.word_tokenize(text))
	freq = nltk.FreqDist(cleanText)
	return freq.most_common(10)

# NLTK token cleansing method which removes stopwords, non alpha words and digits
def NLTKremoveStopwords(tokens):
	tokens = NLTKlowerCaseTokens(tokens)
	return list(filter(lambda word: (word.lower() not in stopwords.words('dutch')) and (word.isalpha() or word.isdigit()) ,tokens))

# Method which lowercases tokens
def NLTKlowerCaseTokens(tokens):
	return [token.lower() for token in tokens]

def writeDictToCSV(fileName, newFile, dictToWrite):
	if not newFile:
		with open(fileName+'.csv', 'a') as f:  # Just use 'w' mode in 3.x
			w = csv.DictWriter(f, dictToWrite.keys())
			w.writerow(dictToWrite)	
	else:
		with open(fileName+'.csv', 'W') as f:  # Just use 'w' mode in 3.x
			w = csv.DictWriter(f, dictToWrite.keys())
			w.writerow(dictToWrite)	

def parseOverzicht():
	succes = 0
	failed = 0
	with open('Overzicht-kamerstukken.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# Create new Kamerstuk
			kamerstuk = Kamerstuk()

			# Process raw link
			rawLink = row['Link '].strip()	
			if "officielebekendmakingen" not in rawLink:
				print ("Document niet zoekbaar: "+row['Titel'])
				continue
			if ".html" in rawLink:
				link = rawLink.replace(".html",".xml")
			elif ".pdf" in rawLink:
				link = rawLink.replace(".pdf",".xml")
			else:
				link = rawLink+".xml"

			# Set link in kamerstuk
			kamerstuk.link= link
			kamerstuk.titel = row['Titel']

			try:
				retrievedKamerstuk = retrieveXML(kamerstuk)

				# Save kamerstuk to file
				writeDictToCSV('kamerstukken-analyse', False, retrievedKamerstuk.getDict())

				succes = succes + 1
			except Exception as error: 
				print(error)
				failed = failed + 1

	print('Succes: '+str(succes))
	print('Failed: '+str(failed))

def countKamerstukRefs():
	global kamerstukken
	ksRefs = {}
	counts = {}

	for ks in kamerstukken:
		for ref in kamerstukken[ks].refs:
			if not ref in ksRefs:
				ksRefs[ref] = [kamerstukken[ks].nummer]
			else:
				ksRefs[ref].append(ref)

	for stuk in ksRefs:
		# Remove duplicates
		counts[stuk] = len(list(dict.fromkeys(ksRefs[stuk])))

		# Write count to file
		with open(fileName+'kamerstukken-count.csv', 'a') as f:  # Just use 'w' mode in 3.x
			w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			w.writerow([stuk, len(list(dict.fromkeys(ksRefs[stuk])))])

	return ksRefs

def retrieveNewKamerstukken(refs):
	searchKS = Kamerstuk()
	for ks in refs:
		if ks in kamerstukken.keys():
			continue
		elif len(refs[ks]) > 1:
			searchKS.link = "https://zoek.officielebekendmakingen.nl/"+ks+".xml"
			try:
				newKS = retrieveXML(searchKS)
				writeDictToCSV('nieuwe-kamerstukken', False, newKS.getDict())
				# newKS.info()
			except:
				print("Failed to search new Kamerstuk")
		

def main():
	parseOverzicht()
	kamerstukkenReferenties = countKamerstukRefs()
	retrieveNewKamerstukken(kamerstukkenReferenties)

if __name__== "__main__":
	main()

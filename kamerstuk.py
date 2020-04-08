class Kamerstuk():
	# Variables shared by all instances

	def __init__(self, nummer="", titel="", kamer="", link="", refs=[], text="", freqTerms=[]):
		# Variables specific to instance
		self.nummer = nummer
		self.titel = titel
		self.kamer = kamer
		self.link = link
		self.refs = refs
		self.text = text
		self.freqTerms = freqTerms

	def info(self):
		print(self.nummer)
		print(self.titel)
		print(self.kamer)
		print(self.link)
		print(self.refs)
		print(self.text)
		print(self.freqTerms)

	def getDict(self):
		return {
			'nummer' : self.nummer,
			'titel' : self.titel,
			'kamer' : self.kamer,
			'link' : self.link,
			'refs' : self.refs,
			'text' : self.text,
			'freqTerms' : self.freqTerms
		}

#https://pypi.python.org/pypi/pdfquery
# http://stackoverflow.com/questions/26748788/extraction-of-text-from-pdf-with-pdfminer-gives-multiple-copies
# We are using pdfMiner http://www.unixuser.org/~euske/python/pdfminer/

# Our aim for this program eventually is the following. We want to input PRD pdf files, get their PACS number, and teach a classifier to predict the PACS number for a new file.
# The way we will go about this is to input a few PRD files, create a bag of words, and store the PACS numbers for each. This will be our training data

from bs4 import BeautifulSoup
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re
from nltk.corpus import stopwords

# This will convert an imported input_file.pdf, and creates an out_put.txt file
def convert(input_file, pages=None):
	open_file = input_file+'.pdf'
	if not pages:
		pagenums = set()
	else:
		pagenums = set(pages)
	output = StringIO()
	manager = PDFResourceManager()
	converter = TextConverter(manager, output, laparams=LAParams())
	interpreter = PDFPageInterpreter(manager, converter)
	infile = file(open_file, 'rb')
	for page in PDFPage.get_pages(infile, pagenums):
		interpreter.process_page(page)
	infile.close()
	converter.close()
	text = output.getvalue()
	output.close
	output_file = 'scraped_'+input_file+'.txt'
	with open(output_file, 'w') as f:	# 'w' for overwriting, and 'a' to not overwrite
		f.write('%s' % text)
	f.close()
	return text

# Takes as an input a .pdf file, and outputs the doi
def doi_finder(search_file, generate_txt):
	if generate_txt is 'yes':
		convert(search_file, pages=None)
	search_file = 'scraped_'+search_file+'.txt'
	search_phrase = 'doi:'
	with open(search_file, "r") as f:
		searchlines = f.readlines()
	for i, line in enumerate(searchlines):
		if search_phrase in line.lower():
			string = searchlines[i]#.lower()[-18:-1:1]		
	for i,j  in enumerate(string):
		if j is ' ':
			string = string[i:i+27]
	string = re.sub("[ \n]", "", string)
	f.close()
	return string

# Takes as an input a .pdf file, and outputs the PACS numbers in a list
def pacs_finder(search_file, generate_txt):
	if generate_txt is 'yes':
		convert(search_file, pages=None)
	search_file = 'scraped_'+search_file+'.txt'
	search_phrase = 'pacs numbers: '
	with open(search_file, "r") as f:
		searchlines = f.readlines()
	for i, line in enumerate(searchlines):
		if search_phrase in line.lower():
			string = searchlines[i][14:]#.lower()
	string = re.sub("[^0-9a-zA-Z.+-,]",           	# The pattern to search for; ^ means NOT
                  			"",                   	# The pattern to replace it with
                          	string )              	# The text to search
	return string.split(',')
'''
	print string.split(',')	
	list_pacs = []
	n = 0
	for i in range(len(string[::8])):
		list_pacs.append(string[n:n+8])
		n = n+8
'''



print doi_finder('Matthias', generate_txt = 'no')
print pacs_finder('Matthias', generate_txt = 'no')


# The following function will take as input the scraped pdf, and will clean it, i.e. keeping the info we want to learn from
def clean_pdf( search_file ):
	text = convert( search_file , pages=None)
#	search_file = 'scraped_'+search_file+'.txt'
#	with open(search_file, "r") as f:
#		searchlines = f.readlines()
	rm_symbol = BeautifulSoup(text).get_text()
	letters_only = re.sub("[^a-zA-Z]", " ", rm_symbol )
	lower_case = letters_only.lower()
	words = lower_case.split()
	stops = set(stopwords.words("english"))
	meaningful_words = [w for w in words if not w in stops]
	meaningful_text = ' '.join(meaningful_words)
	print meaningful_text


#clean_pdf( 'Matthias' )


# The following function will actually learn the bag of words.
def Bag_of_Words(cleaned_reviews, n_features = 5000):
	vectorizer = CountVectorizer(analyzer = "word",
                             tokenizer = None,    	# Allows to tokenize
                             preprocessor = None, 	# Allows to do some preprocessing
                             stop_words = None,   	# We could remove stopwords from here
                             max_features = n_features) 	# Chooses a given number of words, just a subset of the huge total number of words.
	# fit_transform() does two functions: First, it fits the model
	# and learns the vocabulary; second, it transforms our training data
	# into feature vectors. The input to fit_transform should be a list of 
	# strings.
	data_features = vectorizer.fit_transform(cleaned_reviews)
	data_features = data_features.toarray()
	return data_features, vectorizer


# Following was the first code I was using. It uses a different library to scrape the pdf, though it does not work as well, I abandoned it.
'''
import pdfquery
import pdfminer

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

# Open a PDF file.
fp = open('lightNP12.pdf', 'rb')
# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
# Supply the password for initialization.
document = PDFDocument(parser)#, password
# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    print PDFTextExtractionNotAllowed
# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()
# Create a PDF device object.
device = PDFDevice(rsrcmgr)
# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
# Process each page contained in the document.
for page in PDFPage.create_pages(document):
    interpreter.process_page(page)

print document
'''

#https://pypi.python.org/pypi/pdfquery
# http://stackoverflow.com/questions/26748788/extraction-of-text-from-pdf-with-pdfminer-gives-multiple-copies
# We are using pdfMiner http://www.unixuser.org/~euske/python/pdfminer/

# Our aim for this program eventually is the following. We want to input PRD pdf files, get their PACS number, and teach a classifier to predict the PACS number for a new file.
# The way we will go about this is to input a few PRD files, create a bag of words, and store the PACS numbers for each. This will be our training data


from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re

# This will convert an imported input_file.pdf, and creates an out_put.txt file
def convert(input_file, pages=None):
	'''
	Converts a PDF file to blahblah
	'''
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
			string = searchlines[i].lower()#[-18:-1:1]		
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
			string = searchlines[i].lower()[14:]
	string = re.sub("[^0-9a-zA-Z.+-]",           	# The pattern to search for; ^ means NOT
                  			"",                   	# The pattern to replace it with
                          	string )              	# The text to search
	list_pacs = []
	n = 0
	for i in range(len(string[::8])):
		list_pacs.append(string[n:n+8])
		n = n+8
	return list_pacs


print doi_finder('Lutz', generate_txt = 'yes')
print pacs_finder('Lutz', generate_txt = 'no')


# This function will take a bunch of input files, extract useful info, and create a bag of words from which to learn.

#def Bag_of_words():
	


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

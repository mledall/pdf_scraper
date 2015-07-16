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

def doi_finder(search_file, generate_txt):
	if generate_txt is 'yes':
		convert(search_file, pages=None)
	search_file = 'scraped_'+search_file+'.txt'
	search_phrase = 'doi'
	with open(search_file, "r") as f:
		searchlines = f.readlines()
	for i, line in enumerate(searchlines):
		if search_phrase in line.lower():
			string = searchlines[i].lower()#[-18:-1:1]		
	for i,j  in enumerate(string):
		if j is ':':
			string = string[i+1:i+1+27]
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
	string = re.sub("[^0-9a-zA-Z.]",           	# The pattern to search for; ^ means NOT
                  		  "",                   	# The pattern to replace it with
                          string )              	# The text to search
	list_pacs = []
	n = 0
	for i in range(len(string[::8])):
		list_pacs.append(string[n:n+8])
		n = n+8
	return list_pacs

print pacs_finder('Farzan', generate_txt='no')
print doi_finder('Farzan', generate_txt='no')



#https://pypi.python.org/pypi/pdfquery
# http://stackoverflow.com/questions/26748788/extraction-of-text-from-pdf-with-pdfminer-gives-multiple-copies
# We are using pdfMiner http://www.unixuser.org/~euske/python/pdfminer/

# Our aim for this program eventually is the following. We want to input PRD pdf files, get their PACS number, and teach a classifier to predict the PACS number for a new file.
# The way we will go about this is to input a few PRD files, create a bag of words, and store the PACS numbers for each. This will be our training data

import numpy as np
from bs4 import BeautifulSoup
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re
from nltk.corpus import stopwords
from nltk.corpus import words
from sklearn.feature_extraction.text import CountVectorizer

import os
print hello
path = '/home/matthias/Documents/Machine_learning/pdf_scraping'
pdf_files = []


# List all of the .pdf files in the folder
def list_files(path):
	for file in os.listdir(path):
		if file.endswith(".pdf"):
			pdf_files.append(file)
	return pdf_files

# Renames all of the .pdf files in the folder to the appropriate format to be learnt from
def rename_files(path):
	pdf_files = list_files(path)
	for i in range(len(pdf_files)):
		foo = open(pdf_files[i], 'r')
		fname = foo.name
		if ' ' in fname:
			print '%s%d' % (fname.split(' ')[0], i)
			n = '%d' % i
			print fname.split()[0]+'.pdf'
			os.rename(fname, fname.split(' ')[0]+'.pdf')
		foo.close()

rename_files(path)

# This is the set of papers we are using to generate the bag of words. We are only using those papers that can be converting (e.g. not Luty, Baym, Barr, Mohapatra,...), and wich have a PACS number (e.g. not Boixo, Gronau, Wilczek,....)
set_of_papers = ['Aaij','Adam','Aguado','Ahriche','Altmannshofer','Altmannshofer2', 'Anastassov','Anton','Baker','Cacciapaglia','Carrington','Czarnecki','Dib','de_Sousa','de_Sousa2','Dzuba','Faoro', 'Farzan','Griffith', 'Hisano', 'Ibrahim','Klinovaja','Lanting', 'Lutz','Maiezza', 'Matthias', 'Pilaftsis', 'Pilaftsis2','Pilaftsis3', 'Pospelov','Pospelov2','Regan', 'Vives', 'Zimdahl']


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

# Takes as an input a .pdf file, and outputs the doi and PACS numbers. Keep in mind that the doi is not always present in PRD papers. In that case looking for a doi will cause an error
def doi_pacs_finder(search_file, generate_txt):
	if generate_txt is 'yes':
		convert(search_file, pages=None)
	search_file = 'scraped_'+search_file+'.txt'
#	search_doi = 'doi:'
	search_pacs = 'pacs number'
	with open(search_file, "r") as f:
		searchlines = f.readlines()
	for i, line in enumerate(searchlines):
#		if search_doi in line.lower():
#			doi_string = searchlines[i]
		if search_pacs in line.lower():
			pacs_string = searchlines[i]
	pacs_string = re.sub("[^0-9a-zA-Z.+-,:]", "", pacs_string )	#[\n ]
	pacs_string = pacs_string.split(':')[1:][0]
#	doi_string = re.sub("[\n ]", "", doi_string )
#	print 'DOI: {},\nPACS: {}'.format(doi_string.split(':')[1], pacs_string.split(','))
	return pacs_string.split(',')	#doi_string.split(':')[1], 
'''
	print string.split(',')	
	list_pacs = []
	n = 0
	for i in range(len(string[::8])):
		list_pacs.append(string[n:n+8])
		n = n+8
'''

#\u2010\u2011\u2012\u2013\u2014\u2015
#print doi_pacs_finder( 'Luty' , generate_txt = 'no')
#print convert( 'Luty' , pages=None)


# The following function will take as input the scraped pdf, and will clean it, i.e. keeping the info we want to learn from
def clean_pdf( search_file ):
	search_file = 'scraped_'+search_file+'.txt'
	file = open(search_file, 'r')
	text = file.read()
	text_only = BeautifulSoup(text).get_text()
	rm_symbol = re.sub(r'[^\w]', ' ', text_only)
	letters_only = re.sub("[^a-zA-Z]", " ", rm_symbol )
	lower_case = letters_only.lower()
	words_text = set(lower_case.split())
	stops = set(stopwords.words("english"))
	english_words = words.words()
	rm_stopwords = [w for w in words_text if not w in stops]
#	meaningful_words = [w for w in rm_stopwords if w in english_words]	# In order to select the meaningful words, we can either select those that belong to the english dictionary, or instead suppress those that belong to the dictionary, in this way only those terms specific to the subject will count.
# This made me realize, this is an awesome way of fixing typos, look for those words that DO NOT belong to the dictionary!
#	meaningful_words = words - stops
	meaningful_text = ' '.join(rm_stopwords)#meaningful_words
	return meaningful_text


# The following function imports the files, and clean them one by one, and returns a set of all cleaned papers. Right now I am renaming and entering the files by manually, but one day I will code a function that goes to the specified folder, looks at the files, renames them, and do everything else.
def cleaned_papers():
	cleaned_papers = []
	print '- Scraping pdf\'s, cleaning the texts, and creating the Bag of words'
	for i in range(len(set_of_papers)):
		print ' -- {}: Scraping paper {}'.format(i, set_of_papers[i])
		convert(set_of_papers[i], pages=None)
		print ' -- Cleaning paper {}'.format(set_of_papers[i])
		cleaned_papers.append(clean_pdf( set_of_papers[i] ))
		print ' -- PACS: {}'.format(doi_pacs_finder( set_of_papers[i], generate_txt = 'no'))
	return cleaned_papers

# The following function will actually create the bag of words. I think we ought to make a bag of words of all the words that appear across all papers, not just one bag per paper. (This is the technique that was used for the bag of words of the movie reviews.)
def Bag_of_Words(cleaned_papers, n_features = 5000):
#	text = clean_pdf( search_file )
	vectorizer = CountVectorizer(analyzer = "word",
                             tokenizer = None,    	# Allows to tokenize
                             preprocessor = None, 	# Allows to do some preprocessing
                             stop_words = None,   	# We could remove stopwords from here
                             max_features = n_features) 	# Chooses a given number of words, just a subset of the huge total number of words.
	# fit_transform() does two functions: First, it fits the model
	# and learns the vocabulary; second, it transforms our training data
	# into feature vectors. The input to fit_transform should be a list of 
	# strings.
	data_features = vectorizer.fit_transform(cleaned_papers)
	data_features = data_features.toarray()
	return data_features, vectorizer

# Counts the words that appear in the reviews
def word_count():
#	raw_train_data = train_data_import()
#	N_articles = 2000#len(raw_train_data["review"][:])
	papers = cleaned_papers()
	train_data_features, vectorizer = Bag_of_Words(papers)
	vocab = vectorizer.get_feature_names()
	dist = np.sum(train_data_features, axis=0)
	word_count = sorted(zip(dist,vocab),reverse = False)
	for count, tag in word_count:
	    print '{}: {}'.format(count, tag)

def main_function():
#	set_of_papers = ['Ahriche', 'Anastassov', 'Carrington', 'Farzan', 'Hisano', 'Ibrahim', 'Luty', 'Lutz', 'Matthias', 'Pilaftsis', 'Pilaftsis2', 'Pospelov', 'Vives', 'Zimdahl']
#	doi_pacs_finder('Ahriche', generate_txt = 'no')[0]
#	print '{},{}'.format(doi_pacs_finder('Ahriche', generate_txt = 'no')[0], doi_pacs_finder('Ahriche', generate_txt = 'no')[1])
#	print clean_pdf( 'Matthias' )
#	print Bag_of_Words( cleaned_papers() )
#	print cleaned_papers()[1]
	word_count()

main_function()


# piece of code that will be helpful later to read and rename the files automatically.
'''
import os

foo = open("foo.txt", 'wb')
print '%s' % foo.name 
foo.write('That is an interesting file!\n')
foo.write('Yeah no kidding!')
foo.close()

foo = open("foo.txt", 'r')
tezt = foo.read()
print tezt
os.rename('foo.txt', 'bew_foo.txt')
foo.close()

#print os.path.abspath("pdf_scraping/myfile.txt")
path = '/home/matthias/Documents/Machine_learning/pdf_scraping'

#print os.listdir(path)

pdf_files = []

for file in os.listdir(path):
    if file.endswith(".pdf"):
        pdf_files.append(file)

print len(pdf_files), pdf_files
'''


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

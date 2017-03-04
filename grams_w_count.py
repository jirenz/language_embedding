"""
ngram-stats.py :	For given wikipedia dump files (preprocessed by WikiExtractor),
					output the most frequent n-grams for n in [2, k], where k is
					given in input (k = 2 by default).

Usage :	python ngram-stats.py [-k value-of-k] input-directory
"""

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import sanitize_line
from helper import filter_with_alphabet
from nltk import word_tokenize

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz -',
	 type=str, help='supported alphabet')
parser.add_argument('-n', '--ngrams', metavar='n', default=3, type=int, help='store grams up to n')

# Macros and Constants
args = parser.parse_args()
print(args)

print len(args.inputfiles), "files found."

# Add each n-gram (n = gram_length) from texts, into Dict
def add_to_dict(Dict, text, gram_length, debug = False):
	text_length = len(text)
	for i in range(text_length + 1 - gram_length):
		gram = unicode(" ".join(text[i : i + gram_length]))
		if debug: print i, gram
		try:
			Dict[gram] += 1
		except KeyError:
			Dict[gram] = 1

Counter = 0 # Number of articles processed
file_count = 0
for inputfile in args.inputfiles:
	print "Processing file:", inputfile
	dic = {}
	with open(inputfile, "r") as F:
		text = []
		# All articles begin with '<doc' and end with '</doc>'
		for line in F:
			if line.startswith("<doc"):
				continue
			if line.startswith("</doc>"):
				# some paragraph ends
				Counter += 1
				if Counter % 100 == 0:
					print "Finished processing article:", Counter
				continue

			text = word_tokenize(filter_with_alphabet(sanitize_line(line), args.alphabet))
			# text = (filter_with_alphabet(sanitize_line(line), args.alphabet).split())
			for gram_length in range(1, args.ngrams + 1):
				add_to_dict(dic, text, gram_length)
			# cast to unicode string, to lower case, remove non-alphabet characters before processing
			
	#dump the gram info	
	file_name, _ = splitext(basename(inputfile))
	with open(args.outputpath + file_name + ".wgram", "w") as F:
		F.write(json.dumps(dic))

	print "Finish Processing File " + file_name
	file_count += 1
	# clear up
	del dic
# End Processing files

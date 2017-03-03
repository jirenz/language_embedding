"""
ngram-stats.py :	For given wikipedia dump files (preprocessed by WikiExtractor),
					output the most frequent n-grams for n in [2, k], where k is
					given in input (k = 2 by default).

Usage :	python ngram-stats.py [-k value-of-k] input-directory
"""

import sys
import json
from os import listdir
from os.path import isfile, join
import random
import argparse
from helper import remove_nonascii
from helper import filter_with_alphabet

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputpath', type=str, help='input directory that contains all dump files')
parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz ',
	 type=str, help='supported alphabet')
parser.add_argument('-n', '--ngrams', default=3, type=int, help='store grams up to n')
# parser.add_argument('-c', '--numFiles', type=int, help='number of files to process')

# Macros and Constants
args = parser.parse_args()
print(args)
random.seed(args.seed)

# Begin Extract List of files
files = [f for f in listdir(args.inputpath) if isfile(join(args.inputpath, f))]
files.sort()
print len(files), "files found."
# End Extract List of files

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
for file_name in files:
	# if args.numFiles and file_count > args.numFiles:
	# 	break;
	file_path = args.inputpath + "/" + file_name
	print "Processing file:", file_path
	with open(file_path, "r") as F:
		text = []
		dic = {}
		# All articles begin with '<doc' and end with '</doc>'
		for line in F:
			if line.startswith("<doc"):
				continue
			if line.startswith("</doc>"):
				# some paragraph ends
				Counter += 1
				if Counter % 100 == 0:
					print "Going to process article:", Counter
				# print "Going to process article:", Counter, "; this article has", len(text), "words."
				for gram_length in range(1, args.ngrams + 1): # also need single-word appearance
					add_to_dict(dic, text, gram_length)
				del text[:] # **
				# print "Finished processing article:", Counter
				continue	
			# cast to unicode string, to lower case, remove non-alphabet characters before processing
			line = remove_nonascii(line).lower()
			text.extend(filter_with_alphabet(line, args.alphabet).split()) 

	#dump the gram info
	
	# testing file non-existing. Don't want to break things
	#with open(args.outputpath + file_name + ".tgrams", "w") as F:
	#	F.write(json.dumps(dic))

	print "Finish Processing File " + file_name
	file_count += 1
	# clear up
	del dic
# End Processing files

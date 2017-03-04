# TODO: Make it more accurate

import sys
import json
from os import listdir
from os.path import isfile, join
import random

from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(description='Given a n-gram statistic files, generate sub-word sequence info')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
parser.add_argument('-o', '--outputpath', default='./char_seq.grams', type=str, help='output path')
parser.add_argument('-t', '--threashold', default=6, type=int, help='cutoff threshold, inclusive')
# Macros and Constants
args = parser.parse_args()
print(args)

data = {}
counter = 0

def add_char_gram(Dict, text, count, threashold, debug = False):
	if len(text.split(' ')) > 1:
		return
	text_length = len(text)
	for gram_length in xrange(2, threashold + 1):
		for i in range(text_length + 1 - gram_length):
			gram = unicode("".join(text[i : i + gram_length]))
			try:
				Dict[gram] += count
			except KeyError:
				Dict[gram] = count

# Begin Extract List of files
with open(args.outputpath, "w") as output_file:
	print len(args.inputfiles), "files found."
	# End Extract List of files
	for inputfile in args.inputfiles:
		print "Processing file:", inputfile
		with open(inputfile, "r") as F:
			result = json.load(F)
			pbar = tqdm(total=len(result))
			for k,v in result.iteritems():
				add_char_gram(data, k, v, args.threashold)
				pbar.update(1)
			pbar.close()
		counter += 1
		print "Processed ", counter, " files: ", len(data), "entries found"
	output_file.write(json.dumps(data))
# End Processing files
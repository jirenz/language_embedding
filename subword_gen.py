# TODO: Make it more accurate

import sys
import json
from os import listdir
from os.path import isfile, join
import random

import argparse

parser = argparse.ArgumentParser(description='Given a n-gram statistic files, generate sub-word sequence info')
parser.add_argument('inputpath', type=str, help='input directory that contains all dump files')
parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./char_seq.grams', type=str, help='output path')
parser.add_argument('-t', '--threashold', default=5, type=int, help='cutoff threshold, inclusive')

# Macros and Constants
args = parser.parse_args()
print(args)
random.seed(args.seed)

data = {}
counter = 0


def add_char_gram(Dict, gram_in, count, gram_length, debug = False):
	text_arr = gram_in.split(' ')
	for text in text_arr:
		text_length = len(text)
		for i in range(text_length + 1 - gram_length):
			gram = unicode("".join(text[i : i + gram_length]))
			if debug: print i, gram
			try:
				Dict[gram] += count
			except KeyError:
				Dict[gram] = count

# Begin Extract List of files
with open(args.outputpath, "w") as output_file:
	files = [f for f in listdir(args.inputpath) if isfile(join(args.inputpath, f))]
	files.sort()
	print len(files), "files found."
	# End Extract List of files
	for file_name in files:
		if file_name[0] == '.':
			continue
		# if args.numFiles and file_count > args.numFiles:
		# 	break;
		file_path = args.inputpath + "/" + file_name
		print "Processing file:", file_path
		with open(file_path, "r") as F:
			grams = json.load(F)
			for k,v in grams.iteritems():
				for i in xrange(2, args.threashold + 1):
					add_char_gram(data, k, v, i)
				# else:
				# 	pass
				# finally:
				# 	pass
		print "Processed ", counter, " files: ", len(data), "entries found"
	output_file.write(json.dumps(data))
# End Processing files
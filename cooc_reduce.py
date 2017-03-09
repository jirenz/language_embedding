import sys
import json
import os
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
import coocformatter

parser = argparse.ArgumentParser(description='For given wikipedia featured cooc, reduce and shuffle them')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
parser.add_argument('-o', '--outputfile', default='./cooc.shuff.bin', type=str, help='output file')
# parser.add_argument('-s', '--seed', default=12345, help='random seed')
args = parser.parse_args()
print(args)

# Begin Extract List of files
try:
	output_file = open(args.outputfile, "w")
except:
	os.remove(args.outputfile)

print len(args.inputfiles), "files found."
counter = 0
cooc = {}
for inputfile in args.inputfiles:
	counter += 1
	print "Processing file:", inputfile
	with open(inputfile, 'rb') as F:
		while True:
			try:
				word1, word2, val = coocformatter.read_CREC(F)
			except ValueError:
				break
			try:
				cooc[(word1, word2)] += val
			except KeyError:
				cooc[(word1, word2)] = val
			try:
				cooc[(word2, word1)] += val
			except KeyError:
				cooc[(word2, word1)] = val
	print "Processed ", counter, " files: ", len(cooc), "records found"
	keys = cooc.keys()
	randomly_ordered_keys = random.sample(keys, len(cooc))
	with open(args.outputfile, 'wb') as outfile:
		for key in randomly_ordered_keys:
			word1, word2 = key
			coocformatter.write_CREC(outfile, word1, word2, cooc[key])
	print "Finished writing shuffled cooc file"
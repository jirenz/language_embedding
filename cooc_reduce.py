import sys
import json
import os
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
import coocformatter
import pickle

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
	output_file.close()
	os.remove(args.outputfile)
except:
	os.remove(args.outputfile)

print len(args.inputfiles), "files found."
counter = 0
cooc = {}
entry_counter = 0
temp_count = 0
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
			entry_counter += 1
			if entry_counter % 100000 == 0:
				print "Processed", entry_counter, "records"
				if entry_counter % 5000000 == 0:
					print "Dumping", entry_counter, "records to tempfile"
					f_out = open('{}.temp.{}'.format(args.outputfile, temp_count), 'wb')
					pickle.dump(cooc, f_out)
					cooc = {}
					f_out.close()
					temp_count += 1

	print "Processed ", counter, " files: ", len(cooc), "records found"
keys = cooc.keys()
randomly_ordered_keys = random.sample(keys, len(cooc))
with open(args.outputfile, 'wb') as outfile:
	for key in randomly_ordered_keys:
		word1, word2 = key
		coocformatter.write_CREC(outfile, word1, word2, cooc[key])
print "Finished writing shuffled cooc file"
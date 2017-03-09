import sys
import json
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
	output_file = open(args.outputpath, "w")
except:
	os.remove(output_file)

print len(args.inputfiles), "files found."
counter = 0
cooc = {}
for inputfile in args.inputfiles:
	counter += 1
	print "Processing file:", inputfile
	with open(inputfile, 'rb') as F:
		while True:
			try:
				word1, word2, val = coocformatter.read_CREC(f_c)
			except ValueError:
				break
			try:
				all_grams[(word1, word2)] += val
			except KeyError as e:
				all_grams[(word1, word2)] = val
	print "Processed ", counter, " files: ", len(cooc), "records found"
	randomly_ordered_keys = random.sample(cooc.keys, len(cooc))
	with open(outputfile, 'wb') as outfile:
		for key in randomly_ordered_keys:
			word1, word2 = key
			coocformatter.write_CREC(outfile, word1, word2, cooc[key])
	print "Finished writing shuffled cooc file"
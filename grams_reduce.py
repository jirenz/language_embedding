import sys
import json
from os import listdir
from os.path import isfile, join
import random

import argparse

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
parser.add_argument('-o', '--outputpath', default='./collected.grams', type=str, help='output path')

# Macros and Constants
args = parser.parse_args()
print(args)
random.seed(args.seed)

# Begin Extract List of files
with open(args.outputpath, "w") as output_file:
	print len(args.inputfiles), "files found."
	counter = 0
	all_grams = {}
	for inputfile in args.inputfiles:
		# if args.numFiles and file_count > args.numFiles:
		# 	break;
		counter += 1
		print "Processing file:", file_path
		with open(inputfile, "r") as F:
			result = json.load(F)
			for k,v in result.iteritems():
				try:
					all_grams[k] += v
				except KeyError as e:
					all_grams[k] = v
		print "Processed ", counter, " files: ", len(all_grams), "entries found"
	output_file.write(json.dumps(all_grams))
# End Processing files
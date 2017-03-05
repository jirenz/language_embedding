import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random

import argparse

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
# parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
parser.add_argument('-t', '--threashold', default=2, type=int, help='cutoff threshold, inclusive')
# Macros and Constants
args = parser.parse_args()
print(args)

# Begin Extract List of files
print len(args.inputfiles), "files found."
# End Extract List of files
for inputfile in args.inputfiles:
	print "Processing file:", inputfile
	new_result = {}
	with open(inputfile, "r") as F:
		result = json.load(F)
		for k,v in result.iteritems():
			if v > args.threashold:
				new_result[k] = v

	file_name, _ = splitext(basename(inputfile))
	with open(args.outputpath + file_name + ".wgram_trimmed", "w") as F:
		F.write(json.dumps(new_result))
# End Processing files
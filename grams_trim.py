import sys
import json
from os import listdir
from os.path import isfile, join
import random

import argparse

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputpath', type=str, help='input directory that contains all dump files')
parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
parser.add_argument('-t', '--threashold', default=2, type=int, help='cutoff threshold, inclusive')


# Macros and Constants
args = parser.parse_args()
print(args)
random.seed(args.seed)

# Begin Extract List of files
files = [f for f in listdir(args.inputpath) if isfile(join(args.inputpath, f))]
files.sort()
print len(files), "files found."
# End Extract List of files
occur_stats = {}
for file_name in files:
	# if args.numFiles and file_count > args.numFiles:
	# 	break;
	file_path = args.inputpath + "/" + file_name
	print "Processing file:", file_path
	new_result = {}
	with open(file_path, "r") as F:
		result = json.load(F)
		for k,v in result.iteritems():
			if v > args.threashold:
				new_result[k] = v

	with open(args.outputpath + file_name + ".grams", "w") as F:
		F.write(json.dumps(new_result))
# End Processing files
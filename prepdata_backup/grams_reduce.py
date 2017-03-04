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
parser.add_argument('-o', '--outputpath', default='./collected.grams', type=str, help='output path')

# Macros and Constants
args = parser.parse_args()
print(args)
random.seed(args.seed)

# Begin Extract List of files
with open(args.outputpath, "w") as output_file:
	files = [f for f in listdir(args.inputpath) if isfile(join(args.inputpath, f))]
	files.sort()
	print len(files), "files found."
	# End Extract List of files
	counter = 0
	all_grams = {}
	for file_name in files:
		# if args.numFiles and file_count > args.numFiles:
		# 	break;
		counter += 1
		file_path = args.inputpath + "/" + file_name
		print "Processing file:", file_path
		with open(file_path, "r") as F:
			result = json.load(F)
			for k,v in result.iteritems():
				try:
					all_grams[k] += v
				except KeyError as e:
					all_grams[k] = v
				# else:
				# 	pass
				# finally:
				# 	pass
		print "Processed ", counter, " files: ", len(all_grams), "entries found"
	output_file.write(json.dumps(all_grams))
# End Processing files
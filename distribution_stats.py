import sys
import json
from os import listdir
from os.path import isfile, join
import random
import numpy as np

import argparse

parser = argparse.ArgumentParser(description='Given a token-occurrence rate json, generate graph of statistics')
parser.add_argument('inputpath', type=str, help='input directory')
parser.add_argument('-o', '--outputpath', default='./distribution/', type=str, help='output path')
args = parser.parse_args()
print(args)

collections = {}

with open(args.inputpath, "r") as f:
	result = json.load(f)
	print "reading json of length", len(result)
	for k,v in result.iteritems():
		x = int(np.log10(v))
		try:
			arr = collections[x]
			arr.append(k)
		except KeyError:
			collections[x] = []
			collections[x].append(k)

for k,v in collections.iteritems():
	print "bucket", k, "has", len(v), "item(s)"
	# with open(args.outputpath + "_" + str(k) + ".json", 'w') as f:
	# 	f.write(json.dumps(v))
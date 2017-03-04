"""
This file collects all the tokenized articles in a given folder,
generate a raw file (a list of numbers separated by single-space,
for the purpose of training with Glove.

It will concatenate all the sentences/paragraphs/articles with 
single-space. It will ignore all the untraced tokens (number -1).
"""

import sys
from os import listdir
from os.path import isfile, join
import argparse
import random
import json
import re
import numpy as np
from helper import load_data_from_json

parser = argparse.ArgumentParser(description='Tokenize the given article using given gram-set')
parser.add_argument('-i', '--inputpath', default='./Tokenized/Articles', type=str, help='input directory that contains all articles')
parser.add_argument('-o', '--outputpath', default='./Tokenized', type=str, help='output path')
parser.add_argument('outputfile', type=str, help='name of output file')
args = parser.parse_args()
print(args)
inputpath = args.inputpath
outputpath = args.outputpath
outputfile = args.outputfile

#	Begin Extract List of files
articles = [f for f in listdir(inputpath) if isfile(join(inputpath, f))]
articles.sort()
print len(articles), "article files found."

Dict = {}
for article in articles:
	load_data_from_json(Dict, join(inputpath, article))

#	The keys in Dict should be consecutive integers starting from 0. We preserves this order.
with open(join(outputpath, outputfile), "w") as F:
	N = len(Dict)
	for key_int in range(N):
		sentence = Dict[str(key_int)]
		for token in sentence:
			if (token != -1): F.write(str(token) + " ")
	F.write("\n")

	
	

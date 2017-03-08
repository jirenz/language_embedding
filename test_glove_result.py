# This code tests the result of vectors trained by GloVe

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import load_data_from_json

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputfile', default='./data/glove_mar6/vectors.txt', type=str, help='input file')
parser.add_argument('-l', '--labelgram', default='./Tokenized/label_gram.json', type=str, help='output file')
args = parser.parse_args()
print(args)

Dict = {}
load_data_from_json(Dict, args.labelgram)

count = [0, 0, 0, 0, 0, 0]
with open(args.inputfile) as F:
	for line in F:
		idx = (line.split(" "))[0]
		gram = Dict[idx]
		len_gram = len(gram.split(" "))
		count[len_gram] += 1
for i in range(1, 4):
	print str(i) + "-gram appear", count[i], "times."
print "Total:", sum(count), "times."

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import load_data_from_json

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputfile', default='/datadrive/data/glove/vocab.txt', type=str, help='input file')
parser.add_argument('-l', '--labelgram', default='/datadrive/data/wiki_tokenized/label_gram.json', type=str, help='output file')
args = parser.parse_args()
print(args)

Dict = {}
load_data_from_json(Dict, args.labelgram)
print "Loading Dictionary Finished"

threshold = 100
counter = 0
with open(args.inputfile) as F:
	for line in F:
		word, freq = line.split(" ")
		print Dict[word], freq
		counter += 1
		if counter == threshold: break
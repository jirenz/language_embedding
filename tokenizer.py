"""
This file tokenize each sentences in the given file, using a given gram-set.
"""
import sys
from os import listdir
from os.path import isfile, join
import argparse
import random
import json
import re
from dataloader import load_data_from_json

def tokenize(Dict, sentence):
	# core function that will return the parsed sentence as a list of grams
	return sentence.split(" ")
	
parser = argparse.ArgumentParser(description='Tokenize the given article using given gram-set')
parser.add_argument('inputpath', type=str, help='input directory that contains all articles')
parser.add_argument('grampath', type=str, help='input directory that contains all gram-sets')
parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./Tokenized', type=str, help='output path')
parser.add_argument('-p', '--separator', default='[,.;-]', type=str, help='characters that separate sentences')
parser.add_argument('-n', '--number', default=-1, type=int, help='number of gram files we use')

args = parser.parse_args()
print(args)
random.seed(args.seed)

inputpath = args.inputpath
grampath = args.grampath
separator = args.separator
outputpath = args.outputpath

# Begin Extract List of files
articles = [f for f in listdir(inputpath) if isfile(join(inputpath, f))]
articles.sort()
print len(articles), "article files found."

grams = [f for f in listdir(grampath) if isfile(join(grampath, f))]
grams.sort()
print len(grams), "gram files found."
# End Extract List of files

N = args.number
if (N <= 0) or (N >= len(grams)): N = len(grams) # N is the number of gram files we use, after sorted by filename

print "Loading grams dictionary..."
Dict = {} # Global dictionary for gram-files
gram_file_count = 0
for gram_file in grams:
	load_data_from_json(Dict, join(grampath, gram_file))
	gram_file_count += 1
	if (gram_file_count == N): break
print "Loading finished.\n"

Dict_mapping = {} # provide each gram with a unique number as lable
count = 0
for key in Dict:
	count += 1
	Dict_mapping[key] = count
with open(join(outputpath, "grams_label.json"), "w") as F:
	F.write(json.dumps(Dict_mapping))
print "Finish generating mapping from grams to number-label.\n"

print "Begin processing article files..."
article_file_count = 0
for article_file in articles:
	print "Begin processing file", article_file
	# process file, tokenize
	with open(join(inputpath, article_file), "r") as F:
		text = F.readlines()
	sentences = re.split(separator, " ".join(text))
	tokenized_sentences = {} # it's a dictionary with {index:tokenized_sentence} 
	for i in range(len(sentences)):
		tokenized_sentences[i] = tokenize(Dict, sentences[i])
	with open(join(outputpath, article_file + ".readable"), "w") as F:
		F.write(json.dumps(tokenized_sentences))
	# TODO : write the number version
	article_file_count += 1
	print "Finished processing", article_file_count, "file(s)."
	









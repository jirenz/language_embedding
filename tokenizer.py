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
import numpy as np
from dataloader import load_data_from_json

gram_length = 3
token_weight = [0, 1, 10, 13, 16, 19, 22];

def remove_nonascii(text):
	return str(''.join([i if ord(i) < 128 else "" for i in text]))
	
def tokenize(Dict, sentence):
	# core function that will return the parsed sentence as a list of grams
	text = sentence.split(" ")
	result = []
	N = len(text)
	# randomized algorithm
	it = 0
	while (it < N):
		mass = np.zeros(gram_length)
		for i in range(1, gram_length + 1):
			if (it + i <= N):
				mass[i - 1] = Dict.get(" ".join(text[it:it + i]), 1) * token_weight[i] * 1.0
		mass /= sum(mass)
		tmp_len = np.random.choice(gram_length, p = mass) + 1# gram length for this time
		result.append(" ".join(text[it:it + tmp_len]))
		it += tmp_len
	return result
	
def get_gram_label(Dict, sentence):
	# given readable sentence, return labelled version
	result = []
	for gram in sentence:
		result.append(Dict.get(gram, -1))
	return result
	
parser = argparse.ArgumentParser(description='Tokenize the given article using given gram-set')
parser.add_argument('inputpath', type=str, help='input directory that contains all articles')
parser.add_argument('grampath', type=str, help='input directory that contains all gram-sets')
parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
parser.add_argument('-o', '--outputpath', default='./Tokenized', type=str, help='output path')
parser.add_argument('-p', '--separator', default='[,.;]', type=str, help='characters that separate sentences')
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

Dict_gram_to_label = {} # provide each gram with a unique number as lable
Dict_label_to_gram = {}
count = 0
for key in Dict:
	count += 1
	Dict_gram_to_label[key] = count
	Dict_label_to_gram[count] = key
with open(join(outputpath, "gram_label.json"), "w") as F:
	F.write(json.dumps(Dict_gram_to_label))
with open(join(outputpath, "label_gram.json"), "w") as F:
	F.write(json.dumps(Dict_label_to_gram))
print "Finish generating mapping between grams and number-label.\n"

print "Begin processing article files..."
article_file_count = 0
for article_file in articles:
	print "Begin processing file", article_file
	# process file, tokenize
	with open(join(inputpath, article_file), "r") as F:
		text = F.readlines()
	sentences = re.split(separator, remove_nonascii(" ".join(text)))
	tokenized_sentences = {} # it's a dictionary with {index:tokenized_sentence} 
	tokenized_labels = {} 
	for i in range(len(sentences)):
		tmp = tokenize(Dict, sentences[i])
		tokenized_sentences[i] = tmp
		tokenized_labels[i] = get_gram_label(Dict_gram_to_label, tmp)
	with open(join(outputpath, article_file + ".readable"), "w") as F:
		F.write(json.dumps(tokenized_sentences))
	with open(join(outputpath, article_file), "w") as F:
		F.write(json.dumps(tokenized_labels))
	article_file_count += 1
	print "Finished processing", article_file_count, "file(s)."
	









import sys
import random
import json
import re
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from nltk.stem import WordNetLemmatizer

#	This helper function loads a given json file and combine it to the
#	current dictionary. The resulting dictionary can be quite huge.
def load_data_from_json(Dict, filepath):
	# load the json file in filepath
	# combine this json with existing Dict
	with open(filepath, "r") as F:
		data = json.load(F)
		for key in data:
			try:
				Dict[key] += data[key]
			except:
				Dict[key] = data[key]

#	remove non-ascii text in a string
def remove_nonascii(text):
	return str(''.join([i if ord(i) < 128 else "" for i in text]))

#	kepp characters in a string iff it's in the alphabet
#	For training
def filter_with_alphabet(text, alphabet):
	return ''.join(c for c in text if c in alphabet)

#	sanitizes a line read from raw sources
#	For general purposes
def sanitize_line(line):
	return remove_nonascii(line).lower()
	
#	core function that will return the parsed sentence as a list of grams
def tokenize(Dict, sentence, gram_length, token_weight):
	text = sentence.split(" ")
	if text[0] == "":
		text = text[1:]
	result = []
	N = len(text)
	# randomized algorithm, up to change
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

#	Given readable sentence, return labelled version
def get_gram_label(Dict, sentence):
	result = []
	for gram in sentence:
		result.append(Dict.get(gram, -1))
	return result

def write_checkpoint_file(path):
	try:
		from os import environ
		from os.path import join
		if 'SIGNAL_FILE' in environ:
			from datetime import datetime
			i = datetime.now()
			print str(i)
			with open(join(path, environ['SIGNAL_FILE'])) as f:
				f.write()
	except:
		sys.stdout.write("Finished but cannot write signal file")
		pass

def mkdir_p(path):
	import os
	try:
		os.mkdir(path)
	except OSError as exc:  # Python >2.5
		if os.path.isdir(path):
			pass
		else:
			raise
		# if exc.errno == errno.EEXIST and os.path.isdir(path):
		# 	pass
		# else:
		# 	raise

st = WordNetLemmatizer()
def get_wordnet_info(word, context, config):
	#	word: single_word string
	#	context: list of single_word strings
	#	config: Dict of configurations
	#	return: Dict of infos about word
	result = {}
	ss = lesk(context, word)
	if ss is None:
		word = st.lemmatize(word)
		ss = lesk(context, word)
	if ss is None:
		return result

	neighbors = [] # neighbors should be a list of Synset objects
	neighbors.extend(ss.hypernyms())
	neighbors.extend(ss.similar_tos())
	neighbors.extend(ss.also_sees())
	result['neighbors'] = neighbors

	return result

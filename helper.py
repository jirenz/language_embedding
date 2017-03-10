import sys
import random
import json
import re
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
# from nltk.stem import WordNetLemmatizer
# from nltk import pos_tag
# from nltk.corpus import wordnet
import coocformatter

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

# def get_pos_tags(sentence):
# 	return [tag for word, tag in pos_tag(sentence)]

# st = WordNetLemmatizer()
def get_wordnet_info(index, context, context_pos): #, config):
	#	index: center index in context
	#	context: list of single_word strings
	#	contex_pos: list of pos tags for context
	#	config: Dict of configurations Not in use right now
	#	return: Dict of infos about word
	result = {}
	word = context[index]
	pos = get_wordnet_pos(context_pos[index])
	ss = lesk(context, word, pos=pos) # TODO: Apply smoothing
	# No need to lemmatize here because it is called implictly
	# if ss is None:
	# 	print "using lemmatizer"
	# 	word = st.lemmatize(word)
	# 	ss = lesk(context, word)
	if ss is None:
		return None
	result['ss'] = [ss]

	hypernyms = ss.hypernyms()
	if len(hypernyms) > 0:
		result['hypernyms'] = hypernyms

	similar_tos = ss.similar_tos()
	if len(similar_tos) > 0:
		result['similar_tos'] = similar_tos

	also_sees = ss.also_sees()
	if len(also_sees) > 0:
		result['also_sees'] = also_sees
	# neighbors = [] # neighbors should be a list of Synset objects
	# neighbors.extend(ss.hypernyms())
	# neighbors.extend(ss.similar_tos())
	# neighbors.extend(ss.also_sees())
	# result['neighbors'] = neighbors
	return result

def interval_intersect(l1, r1, l2, r2):
	# interval [l1, r1] and [l2, r2]
	if r1 < l2: return False
	if l1 > r2: return False
	return True

# http://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python?noredirect=1&lq=1
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wn.ADJ
    elif treebank_tag.startswith('V'):
        return wn.VERB
    elif treebank_tag.startswith('N'):
        return wn.NOUN
    elif treebank_tag.startswith('R'):
        return wn.ADV
    else:
        return ''

def inc_coocurrence(Dict, label_1, label_2, value):
	if label_1 < 0 or label_2 < 0:
		return
	if label_1 > label_2: label_1, label_2 = label_2, label_1
	try:
		Dict[(label_1, label_2)] += value
	except KeyError:
		Dict[(label_1, label_2)] = value

def process_features(text, featurizer, cooc, window_size):
	features = featurizer.featurize(text)
	N = len(features)
	for center in range(window_size, N):
		# only consider left half, notice that the result matrix is upper-right only
		cur_list = features[center]
		for l in range(center - window_size, center):
			l_list = features[l]
			for token_1 in cur_list:
				for token_2 in l_list:
					if not interval_intersect(token_1["l"], token_1["r"], token_2["l"], token_2["r"]):
						inc_coocurrence(cooc, token_1["val"], token_2["val"], token_1.get("w", 1.) * token_2.get("w", 1.) / (center - l))
	return N

def dump_cooc_to_file(worker_id, cooc, F_out):
	sys.stdout.write("{}: Dumping {} entries\n".format(worker_id, len(cooc)))
	for key, val in cooc.iteritems():
		word1, word2 = key
		coocformatter.write_CREC(F_out, word1, word2, val)
	return

# from nltk.corpus import wordnet
# syns = list(wordnet.all_synsets())
# offsets_list = [(s.offset(), s) for s in syns]
# offsets_dict = dict(offsets_list)

import sys
import random
import json
import re
import numpy as np
from utils import default_gram_length
from helper import get_wordnet_info
from helper import interval_intersect
from helper import get_pos_tags
from featurizer import Featurizer, Settings

window_size = 10
gram_length = default_gram_length

def inc_coocurrence(Dict, label_1, label_2, value):
	if label_1 > label_2: label_1, label_2 = label_2, label_1
	try:
		Dict[(label_1, label_2)] += value
	except KeyError:
		Dict[(label_1, label_2)] = value

def process(text, featurizer, cooc):
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
	return

fragment = "your head look like a ball however hubert has a head which is a polygon this difference derives from the fact that hubert is gamma perturbation stable"
fragment = fragment.split(" ")
all_grams = {}
counter = 0
for word in fragment:
	all_grams[word] = (counter, 0)
	counter += 1
all_grams["your head"] = (counter, 0)
counter += 1
all_grams["a ball"] = (counter, 0)
counter += 1
all_grams["derives from"] = (counter, 0)
counter += 1
featurizer = Featurizer(Settings())
result = {}
process(fragment, featurizer, result)
print result



### DELETED
"""
calc_cooccurence(fragment, all_grams) is a function that will calculate the coocccurence matrix
for a given fragment and dumps the partial result into a dictionary. These dictionaries from
different fragments should be combined to generate the final result.

fragment:	A list of strings/tokens (not integer labels) representing the raw text.
	Note -	Windows crossing fragments will	be ignored; to make the cooccurence result more
			precise, fragment should be a relatively longer list

all_grams:	A dictionary of n-grams (including 1-gram/word) that we will care about. This dict
			is already loaded in memory and passed by reference. It has size 400000.
	Note -	Each entry has format {"gram-string":[unique label, count]}

"""

### NOT IN USE
def get_label(l, r, fragment, all_grams):
	#	Return the list of labels of grams [l, r]; return [] if not found (at most 1 for non-synsets)
	# 	It is guaranteed that (l - window_size) and (r + window_size) are in the range
	result = []
	if l == r:
		#	single word : can be Synset, can be 1-gram
		try:
			label = all_grams[fragment[l]][0]
			result.append(label)
		except KeyError:
			pass

		context = fragment[max(0, l - window_size): min(r + window_size + 1, len(fragment) - 1)]
		tags = get_pos_tags(context) # TODO: only need to calculate once
		wordnet_info = get_wordnet_info(window_size, context, tags)
		if wordnet_info is not None:
			for key, var in wordnet_info.iteritems():
				for ss in var:
					result.append(ss.offset() + synset_global_offset)
	else:
		#	can only appear in all_grams
		gram_string = " ".join(fragment[l: r + 1])
		try:
			label = all_grams[gram_string][0]
			result.append(label)
		except KeyError:
			pass
	return tuple(result)
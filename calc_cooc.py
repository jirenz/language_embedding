import sys
import random
import json
import re
import numpy as np
from utils import default_gram_length
from helper import get_wordnet_info
from helper import interval_intersect
from helper import get_pos_tags

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
synset_global_offset = 400000 # Synset.offset() should add this constant to avoid conflict with entries in all_grams
window_size = 10
gram_length = default_gram_length

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

def inc_coocurrence(Dict, label_1, label_2):
	if label_1 > label_2: label_1, label_2 = label_2, label_1
	try:
		Dict[(label_1, label_2)] += 1
	except KeyError:
		Dict[(label_1, label_2)] = 1

def calc_cooccurence(fragment, all_grams):
	result = {}

	candidates = set() 
	#	Candidates is a set of [left, right] which corresponds to potential n-grams
	#	It filters out those n-grams that in neither all_grams nor wordnet
	#	We need to check interval intersections

	N = len(fragment)
	for l in range(window_size * 2 + 1):
		for length in range(1, 4):
			r = l + length - 1
			if r > window_size * 2 + 1: continue
			labels = get_label(l, r, fragment, all_grams)
			if len(labels) > 0:
				candidates.add((l, r, labels))
	for l in range(window_size, N - gram_length - window_size):
		for length in range(1, 4):
			r = l + length - 1
			labels = get_label(l, r, fragment, all_grams)
			if len(labels) > 0:
				for candidate in candidates:
					#	check candidates and add them to result
					if not interval_intersect(l, r, candidate[0], candidate[1]):
						for label_1 in labels:
							for label_2 in candidate[2]:
								inc_coocurrence(result, label_1, label_2)
		#	update candidates set
		to_remove = []
		for x in candidates:
			if x[0] == l - window_size:
				to_remove.append(x)
		for x in to_remove:
			candidates.remove(x)
		new_r = l + window_size + 1
		for length in range(1, 4):
			new_l = new_r - length + 1
			labels = get_label(new_l, new_r, fragment, all_grams)
			if len(labels) > 0:
				candidates.add((new_l, new_r, labels))
	return result


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
result = calc_cooccurence(fragment, all_grams)
print result
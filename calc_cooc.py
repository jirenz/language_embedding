import sys
import random
import json
import re
import numpy as np
from utils import default_gram_length
from helper import get_wordnet_info
from helper import interval_intersect

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
	#	Return the list of labels of grams [l, r]; return [] if not found (at most 2 for single word, at most 1 for others)
	# 	It is guaranteed that (l - window_size) and (r + window_size) are in the range
	result = []
	if l == r:
		#	single word : can be Synset, can be 1-gram
		try:
			label = all_grams[fragment[l]][0]
			result.append(label)
		except KeyError:
			pass
		# TODO: synset
	else:
		#	can only appear in all_grams
		gram_string = " ".join(fragment[l:r + 1])
		try:
			label = all_grams[gram_string][0]
			result.append(label)
		except KeyError:
			pass
	return result


def calc_cooccurence(fragment, all_grams):
	result = {}

	candidates = set() 
	#	Candidates is a set of [left, right] which corresponds to potential n-grams
	#	It filters out those n-grams that in neither all_grams nor wordnet
	#	We need to check interval intersections

	center = window_size
	for l in range(window_size * 2 + 1):
		for length in range(1, 4):
			r = l + length - 1
			if r > window_size * 2 + 1: continue
			if len(get_label(l, r, fragment, all_grams)) > 0:
				candidates.add((l, r))
	for 


	return result

import sys
import random
import json
import re
import numpy as np

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
def calc_cooccurence(fragment, all_grams):
	result = {}

	return result

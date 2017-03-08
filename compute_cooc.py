# import sys
# import random
# import json
# import re
# import numpy as np
# from helper import sanitize_line
# from helper import filter_with_alphabet
# from helper import interval_intersect



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

def process_wiki_chunk(filename):
	cooc = {}
	all_grams = {}
	text = []
	with open(filename, 'r') as f:
		for line in f:
			if line.startswith("<doc"):
					continue
			if line.startswith("</doc>"):
				process_fragment(text, cooc, all_grams)
				text = []
				# some paragraph ends
				Counter += 1
				# if Counter % 5000 == 0:
					# sys.stdout.write("{}: Finished processing article:{}\n".format(worker_id, Counter))
				# continue
			text.extend(word_tokenize(filter_with_alphabet(sanitize_line(line), args.alphabet)))

def inc_coocurrence(Dict, label_1, label_2):
	if label_1 > label_2: label_1, label_2 = label_2, label_1
	try:
		Dict[(label_1, label_2)] += 1
	except KeyError:
		Dict[(label_1, label_2)] = 1

def process_fragment(fragment, output_dict, settings):
	featurized = featurize(fragment, settings)
	count_cooccurence(featurized, output_dict, settings)

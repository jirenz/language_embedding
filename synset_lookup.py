import sys
import argparse
from nltk.corpus import wordnet as wn
# reader = SynsetReader()

ref_table = {}

print "loading synsets"
for ss in list(wn.all_synsets()):
	ref_table[str(ss.offset())] = ss

while True:
	ss_str = raw_input('Please type synset to look up: ')
	try:
		ss = ref_table[ss.offset()]
		print "definition", ss.definition()
		print "lemmas", ss.lemmas()
	except KeyError:
		print "Not found"
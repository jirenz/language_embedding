from nltk.corpus import wordnet as wn

# wn_pos = []
# wn_pos.append(wn.NOUN)
# wn_pos.append(wn.VERB)
# wn_pos.append(wn.ADJ)
# wn_pos.append(wn.ADV)
ssoffs = []
for ss in list(wn.all_synsets()):
	ssoffs.append(ss.offset())

with open('synset_offset_table.ref', 'w') as f:
	for idx, ssoff in enumerate(ssoffs):
		f.write('{},{}\n'.format(idx, ssoff))

print "found {} synsets".format(len(ssoffs))
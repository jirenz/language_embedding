'''
Trims a cooccurrence file into a cooc matrix with dimensions [V, questioned[V]]
'''

import sys
from struct import Struct
import os
import numpy as np
import coocformatter
import pickle

glove_path = '../../glove'

with open(glove_path + '/vocab.txt', 'r') as f:
	words = [x.rstrip().split(' ')[0] for x in f.readlines()]

print(len(words), "words found")

vocab_size = len(words)
vocab = {w: idx for idx, w in enumerate(words)}
ivocab = {idx: w for idx, w in enumerate(words)}

filenames = [
	'capital-common-countries.txt', 'capital-world.txt', 'currency.txt',
	'city-in-state.txt', 'family.txt', 'gram1-adjective-to-adverb.txt',
	'gram2-opposite.txt', 'gram3-comparative.txt', 'gram4-superlative.txt',
	'gram5-present-participle.txt', 'gram6-nationality-adjective.txt',
	'gram7-past-tense.txt', 'gram8-plural.txt', 'gram9-plural-verbs.txt',
	]
prefix = glove_path + '/eval/question-data/'

used_words = {}
for filename in filenames:
	with open(os.path.join(prefix, filename), 'r') as f:
		full_data = [line.rstrip().split(' ') for line in f]
		for row in full_data:
			for word in row:
				used_words[word] = True
uvocab = {}
iuvocab = {}
counter = 0
for word in used_words:
	uvocab[word] = counter
	iuvocab[counter] = word
	counter += 1

cooc = np.zeros([len(words), len(used_words)])

print('number of used words', len(used_words))
with open('used words', 'w') as f:
	for word in used_words:
		f.write(word)
		f.write('\n')
del words
del used_words

with open(glove_path + '/cooccurrence.shuf.bin', 'rb') as f_c:
	while True:
		try:
			word1, word2, val = coocformatter.read_CREC(f_c)
		except:
			break
		if ivocab[word2 - 1] == 'china' and ivocab[word1 - 1] == 'beijing':
			print 'china', 'beijing', val
		if ivocab[word1 - 1] == 'china' and ivocab[word2 - 1] == 'beijing':
			print 'china', 'beijing', val
		try:
			cooc[word1 - 1][uvocab[ivocab[word2 - 1]]] = val
		except KeyError:
			pass
		try:
			cooc[word2 - 1][uvocab[ivocab[word1 - 1]]] = val
		except KeyError:
			pass
			

np.save('useful_cooc', cooc)
output = open('uvocab_iuvocab_dump', 'wb')
# pickle.dump(uvocab, output)
# pickle.dump(iuvocab, output)
output.close()

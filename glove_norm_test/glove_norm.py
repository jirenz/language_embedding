import sys
from struct import Struct
import os
import numpy as np

with open('../../glove/vocab.txt', 'r') as f:
	words = [x.rstrip().split(' ')[0] for x in f.readlines()]
word_count = {}
with open('../../glove/vocab.txt', 'r') as f:
	for x in f.readlines():
		w, c = x.rstrip().split(' ') 
		word_count[w] = c

print(len(words), "words found")

vocab_size = len(words)
vocab = {w: idx for idx, w in enumerate(words)}
ivocab = {idx: w for idx, w in enumerate(words)}

with open('../../glove/vectors.txt', 'r') as f:
		vectors = {}
		for line in f:
			vals = line.rstrip().split(' ')
			vectors[vals[0]] = [float(x) for x in vals[1:]]

vector_dim = len(vectors[ivocab[0]])
print("vector dimension", vector_dim)

W = np.zeros((vocab_size, vector_dim))
for word, v in vectors.items():
	if word == '<unk>':
		continue
	W[vocab[word], :] = v

d = (np.sum(W ** 2, 1) ** (0.5))


with open('wordcount_norm.csv', 'w') as f:
	for word in word_count:
		f.write("{},{},{}\n".format(word, word_count[word], np.log(word_count[word]), d[vocab[word]]))


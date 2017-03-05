import sys
from struct import Struct
import os
import numpy as np
import coocformatter

with open('../glove/vocab.txt', 'r') as f:
	words = [x.rstrip().split(' ')[0] for x in f.readlines()]

print(len(words), "words found")
cooc = np.zeros([len(words), len(words)])

vocab_size = len(words)
vocab = {w: idx for idx, w in enumerate(words)}
ivocab = {idx: w for idx, w in enumerate(words)}

with open('../glove/vectors.txt', 'r') as f:
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

with open('../glove/cooccurrence.shuf.bin', 'rb') as f_c:
	while True:
		try:
			word1, word2, val = coocformatter.read_CREC(f_c)
		except:
			break
		cooc[word1 - 1][word2 - 1] = val
		cooc[word2 - 1][word1 - 1] = val
exit(0)

def evaluation(predictor, vocab):
	filenames = [
		'capital-common-countries.txt', 'capital-world.txt', 'currency.txt',
		'city-in-state.txt', 'family.txt', 'gram1-adjective-to-adverb.txt',
		'gram2-opposite.txt', 'gram3-comparative.txt', 'gram4-superlative.txt',
		'gram5-present-participle.txt', 'gram6-nationality-adjective.txt',
		'gram7-past-tense.txt', 'gram8-plural.txt', 'gram9-plural-verbs.txt',
		]
	prefix = '../glove/eval/question-data/'

	# to avoid memory overflow, could be increased/decreased
	# depending on system and vocab size
	split_size = 100

	correct_sem = 0; # count correct semantic questions
	correct_syn = 0; # count correct syntactic questions
	correct_tot = 0 # count correct questions
	count_sem = 0; # count all semantic questions
	count_syn = 0; # count all syntactic questions
	count_tot = 0 # count all questions
	full_count = 0 # count all questions, including those with unknown words

	for i in range(len(filenames)):
		with open('%s/%s' % (prefix, filenames[i]), 'r') as f:
			full_data = [line.rstrip().split(' ') for line in f]
			full_count += len(full_data)
			data = [x for x in full_data if all(word in vocab for word in x)]

		indices = np.array([[vocab[word] for word in row] for row in data])
		ind1, ind2, ind3, ind4 = indices.T

		predictions = predictor(ind1, ind2, ind3)

		val = (ind4 == predictions) # correct predictions
		count_tot = count_tot + len(ind1)
		correct_tot = correct_tot + sum(val)
		if i < 5:
			count_sem = count_sem + len(ind1)
			correct_sem = correct_sem + sum(val)
		else:
			count_syn = count_syn + len(ind1)
			correct_syn = correct_syn + sum(val)

		print("%s:" % filenames[i])
		print('ACCURACY TOP1: %.2f%% (%d/%d)' %
			(np.mean(val) * 100, np.sum(val), len(val)))

	print('Questions seen/total: %.2f%% (%d/%d)' %
		(100 * count_tot / float(full_count), count_tot, full_count))
	print('Semantic accuracy: %.2f%%  (%i/%i)' %
		(100 * correct_sem / float(count_sem), correct_sem, count_sem))
	print('Syntactic accuracy: %.2f%%  (%i/%i)' %
		(100 * correct_syn / float(count_syn), correct_syn, count_syn))
	print('Total accuracy: %.2f%%  (%i/%i)' % (100 * correct_tot / float(count_tot), correct_tot, count_tot))

def predictor(wd1, wd2, wd3):
	prediction = np.zeros(wd1.shape)
	for index in xrange(wd1.shape[0]):
		ab = np.matmul(W[wd1[index]].T, W[wd2[index]])
		cd = np.matmul(W, W[wd3[index]].reshape([-1, 1]))
		ad = np.matmul(W, W[wd1[index]].reshape([-1, 1]))
		cb = np.matmul(W[wd3[index]].T, W[wd2[index]])
		prediction[index] = np.argmax(ab + cd  - ad - cb)
	return prediction

def predictor2(wd1, wd2, wd3):
	prediction = np.zeros(wd1.shape)
	for index in xrange(wd1.shape[0]):
		ab = cooc[wd1[index]][wd2[index]]
		cd = cooc[wd3[index]]
		ad = cooc[wd1[index]]
		cb = cooc[wd3[index]][wd2[index]]
		prediction[index] = np.argmax(ab + cd  - ad - cb)

print("evaluating vector")
evaluation(predictor, vocab)
print("evaluating cooc matrix")
evaluation(predictor2, vocab)


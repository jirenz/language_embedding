import numpy as np
import json
import argparse


parser = argparse.ArgumentParser(description='Given a n-gram statistic files, generate sub-word sequence info')
parser.add_argument('vectorfile', metavar='path_to_vector_file', type=str, help='word vectors')
parser.add_argument('label_gram', metavar='label_to_gram_reference', type=str, help='translation table')
parser.add_argument('gram_label', metavar='gram_to_label_reference', type=str, help='translation table')
# parser.add_argument('-o', '--outputpath', default='./char_seq.grams', type=str, help='output path')
args = parser.parse_args()
print(args)

def evaluate_vectors(W, vocab, ivocab):
	"""Evaluate the trained word vectors on a variety of tasks"""

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

		predictions = np.zeros((len(indices),))
		num_iter = int(np.ceil(len(indices) / float(split_size)))
		for j in range(num_iter):
			subset = np.arange(j*split_size, min((j + 1)*split_size, len(ind1)))

			pred_vec = (W[ind2[subset], :] - W[ind1[subset], :]
				+  W[ind3[subset], :])
			#cosine similarity if input W has been normalized
			dist = np.dot(W, pred_vec.T)

			for k in range(len(subset)):
				dist[ind1[subset[k]], k] = -np.Inf
				dist[ind2[subset[k]], k] = -np.Inf
				dist[ind3[subset[k]], k] = -np.Inf

			# predicted word index
			predictions[subset] = np.argmax(dist, 0).flatten()

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

# with open('vocab.txt', 'r') as f:
# 	words = [x.rstrip().split(' ')[0] for x in f.readlines()]
# vocab = {w: idx for idx, w in enumerate(words)}
# ivocab = {idx: w for idx, w in enumerate(words)}
with open('/datadrive/data/glove/vocab.txt', 'r') as f:
	words = [x.rstrip().split(' ')[0] for x in f.readlines()]
vocab_size = len(words)

label_gram = {}
gram_label = {}
with open(args.label_gram, 'r') as F:
	label_gram = json.load(F)
# with open(args.gram_label, 'r') as F:
# 	gram_label = json.load(F)

vocab = {label_gram[w]: idx for idx, w in enumerate(words)}
ivocab = {idx: label_gram[w] for idx, w in enumerate(words)}

with open(args.vectorfile, 'r') as f:
	vectors = {}
	for line in f:
		vals = line.rstrip().split(' ')
		if vals[0] == '<unk>':
			continue
		vectors[label_gram[vals[0]]] = [float(x) for x in vals[1:]]

## Vector is always indexed by number for us so no conversion here
vector_dim = len(vectors[ivocab[0]])

W = np.zeros((vocab_size, vector_dim))
for word, v in vectors.items():
	if word == '<unk>':
		continue
	W[vocab[word], :] = v

W_norm = np.zeros(W.shape)
d = (np.sum(W ** 2, 1) ** (0.5))
W_norm = (W.T / d).T

evaluate_vectors(W_norm, vocab, ivocab)
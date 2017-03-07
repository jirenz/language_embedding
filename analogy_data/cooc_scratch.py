import sys
from struct import Struct
import os
import numpy as np
import coocformatter

glove_path = '../../glove'

words = []
word_count = {}
with open(glove_path + '/vocab.txt', 'r') as f:
	for x in f.readlines():
		word, count = x.rstrip().split(' ')
		words.append(word)
		word_count[word] = count

with open('../glove/vocab.txt', 'r') as f:
	words = [x.rstrip().split(' ')[0] for x in f.readlines()]

print(len(words), "words found")
cooc = np.zeros([len(words), len(words)])

vocab_size = len(words)
vocab = {w: idx for idx, w in enumerate(words)}
ivocab = {idx: w for idx, w in enumerate(words)}


word_log_fre = np.zeros([len(words)], dtype="float32")
for word in word_count:
	word_log_fre[vocab[word]] = float(word_count[word])

word_log_fre = np.log(word_log_fre)

cooc = np.load('useful_cooc.npy')
# print('cooc size', cooc.shape)
# print('row', cooc[0].shape)
# print('col', cooc[:,0].shape)

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
# print len(uvocab), "useful words"

neglect = []
# neglect = ['the', 'in', 'and', 'of', 'is', 'a', 'one', 'to', 'was', 'that', 'for', 'by', 'an']
print len(neglect), "words neglected"
for neg_word in neglect:
	cooc[vocab[neg_word],:] = 0

with open(glove_path + '/vectors.txt', 'r') as f:
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
# cooc_full = np.zeros([len(words), len(words)])
# print "loading cooc matrix"
# with open(glove_path + '/cooccurrence.shuf.bin', 'rb') as f_c:
# 	while True:
# 		count += 1
# 		if count % 10000 == 0:
# 			print "count", count
# 		try:
# 			word1, word2, val = coocformatter.read_CREC(f_c)
# 		except:
# 			break
# 		cooc_full[word1 - 1][word2 - 1] = val
# 		cooc_full[word2 - 1][word1 - 1] = val
# 		# try:
# 		# 	if cooc[vocab[word1]][uvocab[word2]] != val:
# 		# 		print "Error", "cooccur not match", word1, word2
# 		# 	exit(-1)
# 		# except KeyError:
# 		# 	pass
# 		# try:
# 		# 	if cooc[vocab[word2]][uvocab[word1]] != val:
# 		# 		print "Error", "cooccur not match", word2, word1
# 		# 	exit(-1)
# 		# except KeyError:
# 		# 	pass

top_n = int(sys.argv[1])
if top_n == None:
	top_n = 1

def dump_pred(file, ivocab, wd1, wd2, wd3, wd4, predictions):
	for index in xrange(len(wd1)):
		file.write("{}, {}, {}, {}, {}\n".format(ivocab[wd1[index]], ivocab[wd2[index]], 
			ivocab[wd3[index]], ivocab[wd4[index]], ivocab[predictions[index]]))


def evaluation(predictor, vocab, ivocab, result_file):
	filenames = [
		'capital-common-countries.txt', 'capital-world.txt', 'currency.txt',
		'city-in-state.txt', 'family.txt', 'gram1-adjective-to-adverb.txt',
		'gram2-opposite.txt', 'gram3-comparative.txt', 'gram4-superlative.txt',
		'gram5-present-participle.txt', 'gram6-nationality-adjective.txt',
		'gram7-past-tense.txt', 'gram8-plural.txt', 'gram9-plural-verbs.txt',
		]
	prefix = glove_path + '/eval/question-data/'

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

		dump_pred(result_file, ind1, ind2, ind3, ind4, predictions)

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
		counted = ab + cd  - ad - cb
		counted[wd1[index]] = -np.Inf
		counted[wd2[index]] = -np.Inf
		counted[wd3[index]] = -np.Inf

		prediction[index] = np.argmax(counted)
	return prediction

def predictor2(wd1, wd2, wd3):
	prediction = np.zeros(wd1.shape)
	for index in xrange(wd1.shape[0]):
		ab = cooc[wd1[index]][wd2[index]]
		cd = cooc[wd3[index]]
		ad = cooc[wd1[index]]
		cb = cooc[wd3[index]][wd2[index]]
		counted = ab + cd  - ad - cb
		counted[wd1[index]] = -np.Inf
		counted[wd2[index]] = -np.Inf
		counted[wd3[index]] = -np.Inf

		prediction[index] = np.argmax(counted)
	return prediction


def predictor3(wd1, wd2, wd3):
	split_size = 100
	W_norm = np.zeros(W.shape)
	d = (np.sum(W ** 2, 1) ** (0.5))
	W_norm = (W.T / d).T

	predictions = np.zeros((len(wd1),))
	num_iter = int(np.ceil(len(wd1) / float(split_size)))
	for j in range(num_iter):
		subset = np.arange(j*split_size, min((j + 1)*split_size, len(wd1)))

		pred_vec = (W_norm[wd2[subset], :] - W_norm[wd1[subset], :]
			+  W_norm[wd3[subset], :])
		#cosine similarity if input W has been normalized
		dist = np.dot(W_norm, pred_vec.T)

		for k in range(len(subset)):
			dist[wd1[subset[k]], k] = -np.Inf
			dist[wd2[subset[k]], k] = -np.Inf
			dist[wd3[subset[k]], k] = -np.Inf

		# predicted word index
		predictions[subset] = np.argmax(dist, 0).flatten()
	return predictions

with open('eva_coocmatrix.txt', 'w') as F:
	print("evaluating cooc matrix")
	evaluation(predictor2, vocab, ivocab, F)
# with open('eva_vector.txt', 'w') as F:
# 	print("evaluating vector")
# 	evaluation(predictor, vocab, ivocab, F)
with open('eva_norm_vector.txt', 'w') as F:
	print("evaluating normalized vector")
	evaluation(predictor3, vocab, ivocab, F)


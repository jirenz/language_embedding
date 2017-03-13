import numpy as np
import json
import argparse
from os.path import join

def dump_pred(file, ivocab, wd1, wd2, wd3, wd4, predictions):
	for index in xrange(len(wd1)):
		file.write("{}, {}, {}, {}, {}\n".format(ivocab[wd1[index]], ivocab[wd2[index]], 
			ivocab[wd3[index]], ivocab[wd4[index]], [ivocab[prediction[index]] for prediction in predictions]))


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

		dump_pred(result_file, ivocab, ind1, ind2, ind3, ind4, predictions)


		val = np.zeros(ind4.shape)
		for ques_index in xrange(ind4.shape[0]):
			for pred_index in xrange(args.top):
				if ind4[ques_index] == predictions[pred_index][ques_index]:
					val[ques_index] = 1 # correct predictions
		count_tot = count_tot + len(ind1)
		correct_tot = correct_tot + sum(val)
		if i < 5:
			count_sem = count_sem + len(ind1)
			correct_sem = correct_sem + sum(val)
		else:
			count_syn = count_syn + len(ind1)
			correct_syn = correct_syn + sum(val)

		print("%s:" % filenames[i])
		print('ACCURACY TOP%d: %.2f%% (%d/%d)' %
			(args.top, np.mean(val) * 100, np.sum(val), len(val)))

	print('Questions seen/total: %.2f%% (%d/%d)' %
		(100 * count_tot / float(full_count), count_tot, full_count))
	print('Semantic accuracy: %.2f%%  (%i/%i)' %
		(100 * correct_sem / float(count_sem), correct_sem, count_sem))
	print('Syntactic accuracy: %.2f%%  (%i/%i)' %
		(100 * correct_syn / float(count_syn), correct_syn, count_syn))
	print('Total accuracy: %.2f%%  (%i/%i)' % (100 * correct_tot / float(count_tot), correct_tot, count_tot))

def predictor(wd1, wd2, wd3):
	predictions = []
	for i in xrange(args.top):
		predictions.append(np.zeros(wd1.shape))
	
	# num_iter = int(np.ceil(len(wd1) / float(split_size)))
	for index in xrange(wd1.shape[0]):
	# for j in range(num_iter):
		# subset = np.arange(j*split_size, min((j + 1)*split_size, len(wd1)))

		pred_vec = (W_norm[wd2[index], :] - W_norm[wd1[index], :]
			+  W_norm[wd3[index], :])
		#cosine similarity if input W has been normalized
		dist = np.dot(W_norm, pred_vec.T)

		dist[wd1[index]] = -np.Inf
		dist[wd2[index]] = -np.Inf
		dist[wd3[index]] = -np.Inf

		# if args.first > 0:
		# 	for rm_index in xrange(wd1.shape[0]):
		# 		if rm_index >= args.first:
		# 			dist[rm_index] = -np.Inf

		# predicted word index
		for i in xrange(args.top):
			if i > 0:
				dist[predictions[i - 1][index]] = -np.Inf
			predictions[i][index] = np.argmax(dist)
		# predictions[subset] = np.argmax(dist, 0).flatten()
	return predictions


parser = argparse.ArgumentParser(description='evaluate trained vectors')
parser.add_argument('path', metavar='path_to_vector_file_and_vocab_file', type=str, help='filepath')
parser.add_argument('--top', '-t', metavar='top_n', type=int, default=1, help='show top n results for the analogy test')
parser.add_argument('--first', '-f', metavar='first_k', type=int, default=-1, help='use first k words in the vocab, -1 to use all')
args = parser.parse_args()
print(args)

glove_path = '../glove'

filenames = [
	'capital-common-countries.txt', 'capital-world.txt', 'currency.txt',
	'city-in-state.txt', 'family.txt', 'gram1-adjective-to-adverb.txt',
	'gram2-opposite.txt', 'gram3-comparative.txt', 'gram4-superlative.txt',
	'gram5-present-participle.txt', 'gram6-nationality-adjective.txt',
	'gram7-past-tense.txt', 'gram8-plural.txt', 'gram9-plural-verbs.txt',
	]
prefix = glove_path + '/eval/question-data/'

words = []
with open(join(args.path+'vocab.txt'), 'r') as F:
	for line in F:
		words.append(line.strip().split()[0])
		if args.first > 0 and len(words) > args.first:
			break;
vocab_size = len(words)
print("vocab size", vocab_size)

ivocab = {}
vocab = {}
for idx, token in enumerate(words):
	vocab[token] = idx
	ivocab[idx] = token


with open(join(args.path+'vectors.txt'), 'r') as f:
	vectors = {}
	for line in f:
		vals = line.rstrip().split(' ')
		try:
			vectors[vals[0]] = [float(x) for x in vals[1:]]
		except KeyError:
			print "got unkown key: ", vals[0]
			continue
		except ValueError:
			print vals
			exit(0)

vector_dim = len(vectors[ivocab[0]])

print("vector dimension", vector_dim)

W = np.zeros((vocab_size, vector_dim))
for index, v in vectors.items():
	try:
		W[vocab[index], :] = v
	except:
		print "unknown index", index
		continue


W_norm = np.zeros(W.shape)
d = (np.sum(W ** 2, 1) ** (0.5))
zero_count = 0
for index in xrange(d.shape[0]):
	if d[index] == 0:
		zero_count += 1
		d[index] = 1
print("In total {} zero vectors", zero_count)

W_norm = (W.T / d).T


with open('analogy_results_top{}.txt'.format(args.top), 'w') as F:
 	print("evaluating vectors")
 	evaluation(predictor, vocab, ivocab, F)

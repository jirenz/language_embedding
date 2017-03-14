import tensorflow as tf
import numpy as np
import sys
import argparse
from featurizer import Featurizer
# from dataloader import Loader
from language_model import Config, Model
from operator import add
from random import shuffle
from tqdm import tqdm
import pickle

class Loader():
	def __init__(self, featurizer, path = 'sentiment_data/'):
		self.path = path
		self.featurizer = featurizer


	def load_raw(self, num_features=30):
		path = self.path
		print "loading raw data"
		self.train_raw = self.read_sentence(path + 'train.txt')
		self.dev_raw = self.read_sentence(path + 'dev.txt')
		self.test_raw = self.read_sentence(path + 'test.txt')
		print "featurizing"
		self.train = self.featurize_data(self.train_raw, num_features)
		self.dev = self.featurize_data(self.dev_raw, num_features)
		self.test = self.featurize_data(self.test_raw, num_features)
		with open(path + 'train.bin', 'wb') as f:
			pickle.dump(self.train, f)
		with open(path + 'test.bin', 'wb') as f:
			pickle.dump(self.test, f)
		with open(path + 'dev.bin', 'wb') as f:
			pickle.dump(self.dev, f)

	def load(self, num_features=30):
		path = self.path
		print "loading data"
		with open(path + 'train.bin', 'rb') as f:
			self.train = pickle.load(f)
		with open(path + 'test.bin', 'rb') as f:
			self.test = pickle.load(f)
		with open(path + 'dev.bin', 'rb') as f:
			self.dev = pickle.load(f)

	def read_sentence(self, file):
		data = []
		with open(file, 'r') as f:
			for line in f:
				tokens = line.split(' ')
				data.append([tokens[0], " ".join(tokens[1:])])
		return data

	def featurize_data(self, data, num_features):
		labels = []
		features = []
		masks = []
		pbar = tqdm(total=len(data))
		for label, sentence in data:
			feature, mask = self.featurize_sentence(sentence, num_features)
			labels.append(label)
			features.append(feature)
			masks.append(mask)
			pbar.update(1)
		pbar.close()
		length = len(labels)
		labels = np.array(labels, dtype="int32")
		features = np.array(features, dtype="int32")
		masks = np.array(masks, dtype="float32")
		return labels, features, masks

	def featurize_sentence(self, sentence, num_features):
		features = featurizer.featurize(sentence)
		features = reduce(add, features)
		shuffle(features)
		feature_vec = np.zeros([num_features], dtype="int32")
		mask_vec = np.zeros([num_features], dtype="int32")
		count = 0
		for feature in features:
			if feature['t'] != 'pos' and count < num_features:
				if feature['val'] == -1:
					continue
				feature_vec[count] = feature['val']
				mask_vec[count] = feature.get('w', 1.)
				count += 1
				# TODO: pos tags? random dropout?
		return feature_vec, mask_vec
		# for feature in features:
		# 	if feature['t'] != 'pos' && count < num_features:
		# 		feature_vec[count] = feature.['val']
		# 		feature_mask[count] = feature.get('w', default=1.)

def test(data, session):
	print "testing"
	labels, features, masks = data
	length = labels.shape[0]
	batch_size = 2
	indexes = np.random.shuffle(np.arange(labels.shape[0]))
	predictions = np.zeros(labels.shape)
	predictions = np.argmax(model.predict_on_batch(session, (features, masks)), axis=1)
	correct = np.sum(np.eq(predictions, labels))
	print "correct: {}/{}, {}%".format(correct, length, 100 * correct / length)

def train(data, session, epochs=5, batch_size=5):
	labels, features, masks = data
	indexes = np.arange(labels.shape[0])
	np.random.shuffle(indexes)
	loss = 0
	for batch in tqdm(xrange(int(labels.shape[0] / batch_size))):
		# print indexes[batch * batch_size: (batch + 1) * batch_size]
		label = labels[indexes[batch * batch_size: (batch + 1) * batch_size]]
		feature = features[indexes[batch * batch_size: (batch + 1) * batch_size]]
		mask = masks[indexes[batch * batch_size: (batch + 1) * batch_size]]
		loss += model.train_on_batch(session, (feature, mask), label)
	loss /= int(labels.shape[0] / batch_size)
	print "loss:{}".format(loss)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
			generate dump of article n-gram statistics')
	parser.add_argument('-e', '--embedding', type=str, help='path to embedding txt')
	parser.add_argument('--raw', action='store_true')
	args = parser.parse_args()
	print args

	
	with tf.Graph().as_default():
		config = Config()
		featurizer = Featurizer()
		
		model = Model(config)
		loader = Loader(featurizer)
		
		if args.raw: # prep data
			loader.load_raw()
			exit(0)
		
		embeddings, embed_size = featurizer.labeler.load_embedding(args.embedding)
		config.dim_embedding = embed_size
		loader.load()
		model.add_embeddings(embeddings)
		model.build()
	
		init = tf.global_variables_initializer()
		# saver = tf.train.Saver()
		with tf.Session() as session:
			session.run(init)
			epochs = 5
			for epoch in xrange(epochs):
				print "epoch: {}".format(epoch)
				train(loader.train, session)
				test(loader.dev, session)
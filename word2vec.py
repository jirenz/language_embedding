import tensorflow as tf
import numpy as np
import logging
from model_ref import model
from dataloader import load_data
from tqdm import tqdm
import pickle

class Config:
	"""Holds model hyperparams and data information.

	The config class is used to store various hyperparameters and dataset
	information parameters. Model objects are passed a Config() object at
	instantiation.
	"""

	dim_V = 123456 # vocabulary size
	dim_H = 300 # embedding size
	window_size = 6
	n_epochs = 10
	batch_size = 50
	lr = 0.001
	n_epochs = 10

	# n_word_features = 2 # Number of features for every word in the input.
	# window_size = 1
	# n_features = (2 * window_size + 1) * n_word_features # Number of features for every word in the input.
	# max_length = 120 # longest sequence to parse
	# n_classes = 5
	# dropout = 0.5
	# embed_size = 50
	# hidden_size = 300
	# batch_size = 32
	# n_epochs = 10
	# max_grad_norm = 10.
	# lr = 0.001
	# 

class Word2VecModel(Model):
	def __init__(config):
		self.add_placeholders()
		self.add_prediction_op()
		self.add_loss_op()
		self.add_training_op()
		self.config = config

	def add_placeholders(self):
		"""Adds placeholder variables to tensorflow computational graph.

		Tensorflow uses placeholder variables to represent locations in a
		computational graph where data is inserted.  These placeholders are used as
		inputs by the rest of the model building and will be fed data during
		training.

		See for more information:
		https://www.tensorflow.org/versions/r0.7/api_docs/python/io_ops.html#placeholders
		"""
		self.inputs = tf.placeholder("float32", [None, self.config.dim_V])
		self.labels = tf.placeholder("float32", [None, self.config.dim_V])
		return

	def create_feed_dict(self, inputs_batch, labels_batch=None):
		"""Creates the feed_dict for one step of training.

		A feed_dict takes the form of:
		feed_dict = {
				<placeholder>: <tensor of values to be passed for placeholder>,
				....
		}

		If labels_batch is None, then no labels are added to feed_dict.

		Hint: The keys for the feed_dict should be a subset of the placeholder
					tensors created in add_placeholders.
		Args:
			inputs_batch: A batch of input data. It is an array of feature vectors
			labels_batch: A batch of label data.
		Returns:
			feed_dict: The feed dictionary mapping from placeholders to values.
		"""
		feed_dict = {
			self.inputs = inputs_batch
		}
		if labels_batch:
			feed_dict[self.lables] = labels_batch
		return

	def add_prediction_op(self):
		"""Implements the core of the model that transforms a batch of input data into predictions.

		Returns:
			pred: A tensor of shape (batch_size, window_size, dim_V)
		"""
		self.embedding_in = tf.Variable(tf.zeros([self.config.dim_V, self.config.dim_H]), name="vector_in")
		self.embedding_out = tf.Variable(tf.zeros([self.config.dim_V, self.config.dim_H]), name="vector_out")
		self.pred = tf.matmul(self.embedding_out, tf.matmul(self.inputs, self.embedding_in))
		return self.pred

	def add_loss_op(self):
		"""Adds Ops for the loss function to the computational graph.

		Args:
			pred: A tensor of shape (batch_size, n_classes)
		Returns:
			loss: A 0-d tensor (scalar) output
		"""
		self.loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.labels, logits=self.pred))
		return self.loss

	def add_training_op(self, loss):
		"""Sets up the training Ops.

		Creates an optimizer and applies the gradients to all trainable variables.
		The Op returned by this function is what must be passed to the
		sess.run() to train the model. See

		https://www.tensorflow.org/versions/r0.7/api_docs/python/train.html#Optimizer

		for more information.

		Args:
			loss: Loss tensor (a scalar).
		Returns:
			train_op: The Op for training.
		"""
		opt = tf.train.AdamOptimizer(learning_rate=self.config.lr)
		self.train_op = opt.minimize(loss)
		return self.train_op

	def train_on_batch(self, sess, inputs_batch, labels_batch):
		"""Perform one step of gradient descent on the provided batch of data.
		This version also returns the norm of gradients.
		"""
		feed = self.create_feed_dict(inputs_batch, labels_batch=labels_batch)
		_, loss = sess.run([self.train_op, self.loss], feed_dict=feed)
		return loss

	def fit(session, saver, train, dev):
		for epoch in self.config.n_epochs:
			logger.info("epoch: %d", epoch)
			pbar = tqdm(total=len(train))
			loss = 0
			for batch in train:
				loss += self.train_on_batch(session)
				pbar.update(1)
			pbar.close()
			loss /= len(train)
			logger.info("loss: %f", loss)

	def get_embedding(session):
		embedding_in, embedding_out = sess.run([self.embedding_in, self.embedding_out])
		return embedding_in, embedding_out


def main():
	logger = logging.getLogger('main')
	with tf.Graph().as_default():
		logger.info("Building model...",)
		start = time.time()
		model = Word2VecModel(config)
		logger.info("took %.2f seconds", time.time() - start)

		logger.info("Loading and preparing data...",)
		start = time.time()
		train, dev = loaddata()
		logger.info("took %.2f seconds", time.time() - start)

		init = tf.global_variables_initializer()
		saver = tf.train.Saver()

		with tf.Session() as session:
			session.run(init)
			model.fit(session, saver, train, dev)
			embedding_in, embedding_out = model.get_embedding(session)
			numpy.save('embedding in', embedding_in)
			numpy.save('embedding out', embedding_out)


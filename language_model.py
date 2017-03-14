import logging
import tensorflow as tf

class Config:
	"""Holds model hyperparams and data information.
	The config class is used to store various hyperparameters and dataset
	information parameters. Model objects are passed a Config() object at
	instantiation.
	"""
	dim_V = 4 # vocabulary size
	dim_embedding = 100
	dim_H = 300 # embedding size
	num_layers = 3
	signal_size_in = 30
	dim_pred = 5
	# signal_size_out = 20
	# signal_size_neg = 20

class Model(object):
	"""Abstracts a Tensorflow graph for a learning task.

	We use various Model classes as usual abstractions to encapsulate tensorflow
	computational graphs. Each algorithm you will construct in this homework will
	inherit from a Model object.
	"""
	def __init__(self,config):
		self.config = config
		self.logger = logging.getLogger('language_model')

	
	def add_placeholders(self):
		"""Adds placeholder variables to tensorflow computational graph.

		Tensorflow uses placeholder variables to represent locations in a
		computational graph where data is inserted.  These placeholders are used as
		inputs by the rest of the model building and will be fed data during
		training.

		See for more information:
		https://www.tensorflow.org/versions/r0.7/api_docs/python/io_ops.html#placeholders
		"""
		self.inputs = tf.placeholder(dtype=tf.int32, shape=[None, self.config.signal_size_in], name="inputs")
		self.input_masks = tf.placeholder(dtype=tf.float32, shape=[None, self.config.signal_size_in], name="input_masks")
		self.labels = tf.placeholder(dtype=tf.int32, shape=[None], name="labels")
		# self.labels = tf.placeholder("int", [None, self.config.signal_size_out], name="labels")
		# self.neg_labels = tf.placeholder("int", [None, self.config.signal_size_neg], name="negative_labels")

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
			inputs_batch: A batch of input data.
			labels_batch: A batch of label data.
		Returns:
			feed_dict: The feed dictionary mapping from placeholders to values.
		"""
		feed_dict = {}
		feed_dict[self.inputs], feed_dict[self.input_masks] = inputs_batch
		if labels_batch is not None:
			feed_dict[self.labels] = labels_batch
		return feed_dict

	def add_embeddings(self,embeddings):
		if embeddings is None:
			self.embeddings = tf.Variable(tf.random_normal([self.config.dim_V, self.config.dim_embedding], stddev=0.1), name="embeddings")
		else:
			self.embeddings = tf.Variable(embeddings, dtype=tf.float32, name="embeddings")

	def add_variables(self):
		self.Ws = [tf.Variable(tf.random_normal([self.config.dim_embedding, self.config.dim_H], dtype=tf.float32, stddev=0.1), name="embedding_to_hidden")]
		self.Bs = [tf.Variable(tf.zeros([self.config.dim_H], dtype=tf.float32), name="embedding_to_hidden_bias")]
		for i in xrange(1, self.config.num_layers):
			self.Ws.append(tf.Variable(tf.random_normal([self.config.dim_H, self.config.dim_H], stddev=0.1, dtype=tf.float32), name="hidden_{}".format(i)))
			self.Bs.append(tf.Variable(tf.zeros(self.config.dim_H, dtype=tf.float32), name="hidden_{}_bias".format(i)))

	def linear(self, a, b, c, name=None):
		return tf.add(tf.matmul(a, b), c, name=name)

	def non_linear(self, a,b,c):
		return tf.nn.relu(self.linear(a,b,c))

	def add_layers(self):
		"""Implements the core of the model that transforms a batch of input data into predictions.
		! requires add_variables and add_embedding
		inputs batch * signal_size_in
		collected_embeddings batch * signal_size_in * dim_embedding
		masked_embeddings batch * signal_size_in * dim_embedding
		summed_embeddings batch * dim_embedding
		Returns:
			pred: A tensor of shape (batch_size, n_classes)
		"""
		self.collected_embeddings = tf.gather(self.embeddings, self.inputs, name="collected_embeddings")
		self.normalized_masks = tf.divide(self.input_masks, tf.reduce_sum(self.input_masks), name="normalized_masks")
		self.normalized_masks = tf.reshape(self.normalized_masks, [-1, self.config.signal_size_in, 1], name="reshape_normalized_masks")
		self.masked_embeddings = tf.multiply(self.collected_embeddings, self.normalized_masks, name="masked_embeddings")
		self.summed_embeddings = tf.reduce_sum(self.masked_embeddings, axis=1, name="sum_embeddings")
		self.activations = [self.linear(self.summed_embeddings, self.Ws[0], self.Bs[0])]
		for i in xrange(1, self.config.num_layers):
			self.activations.append(self.non_linear(self.activations[i - 1], self.Ws[i], self.Bs[i]))
		self.activation_out = self.activations[-1]

	def add_prediction_op(self):
		self.pred_W = tf.Variable(tf.random_normal([self.config.dim_H, self.config.dim_pred], stddev=0.1, dtype=tf.float32), name="pred_W")
		self.pred_B = tf.Variable(tf.zeros([self.config.dim_pred], dtype=tf.float32), name="pred_B")
		self.hat_y = self.linear(self.activation_out, self.pred_W, self.pred_B, name="hat_y")
		self.pred = tf.nn.softmax(self.hat_y)

	def add_loss_op(self):
		"""Adds Ops for the loss function to the computational graph.

		Args:
			pred: A tensor of shape (batch_size, n_classes)
		Returns:
			loss: A 0-d tensor (scalar) output
		"""
		self.loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=self.labels, logits=self.hat_y, name="softmax_ce_loss")

	def add_training_op(self):
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
		opt = tf.train.AdamOptimizer() # learning_rate=self.config.lr)
		self.train_op = opt.minimize(self.loss)

	def train_on_batch(self, sess, inputs_batch, labels_batch):
		"""Perform one step of gradient descent on the provided batch of data.

		Args:
			sess: tf.Session()
			input_batch: np.ndarray of shape (n_samples, n_features)
			labels_batch: np.ndarray of shape (n_samples, n_classes)
		Returns:
			loss: loss over the batch (a scalar)
		"""
		feed = self.create_feed_dict(inputs_batch, labels_batch=labels_batch)
		_, loss = sess.run([self.train_op, self.loss], feed_dict=feed)
		return loss

	def predict_on_batch(self, sess, inputs_batch):
		"""Make predictions for the provided batch of data

		Args:
			sess: tf.Session()
			input_batch: np.ndarray of shape (n_samples, n_features)
		Returns:
			predictions: np.ndarray of shape (n_samples, n_classes)
		"""
		feed = self.create_feed_dict(inputs_batch)
		predictions = sess.run(self.pred, feed_dict=feed)
		return predictions

	"""
	Need to initialize embeddings first
	"""
	def build(self):
		self.add_placeholders()
		self.add_variables()
		self.add_layers()
		self.add_prediction_op()
		self.add_loss_op()
		self.add_training_op()

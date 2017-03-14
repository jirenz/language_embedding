import tensorflow as tf
import numpy as np
import sys
import argparse
from featurizer import Featurizer
# from dataloader import Loader
from language_model import Config, Model



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
			generate dump of article n-gram statistics')
	parser.add_argument('-e', '--embedding', type=str, help='path to embedding txt')
	args = parser.parse_args()
	print args

	config = Config()
	featurizer = Featurizer()
	embeddings, embed_size = featurizer.labeler.load_embedding(args.embedding)
	config.dim_embedding = embed_size
	model = Model(config)
	model.add_embeddings(embeddings)
	model.build()
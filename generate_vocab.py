from featurizer import FeatureLabeler
import sys

l = FeatureLabeler()

l.generate_vocab_file(sys.argv[1])
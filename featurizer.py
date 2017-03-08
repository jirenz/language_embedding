from utils import default_gram_length
from helper import get_wordnet_info
from helper import get_pos_tags
from helper import get_wordnet_pos
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk


'''
Requirement:
	all grams: {string: True/data}
	We only need keys here
'''

class Settings():
	def __init__(self, all_grams, ss_weight=None):
		if ss_weight is None:
			ss_weight = {
				'self': 1,
				'hyper': 0.5,
				'sim': 1,
				'also': 1
			}
		self.all_grams = all_grams
		self.ss_weight = ss_weight
		self.gram_length = default_gram_length
		self.lesk_width = 5


class Featurizer():
	def __init__(self, settings):
		self.settings = settings

	def get_feature_pos(self, fragment, features):
		tagged = pos_tag(fragment)
		for index in xrange(len(tagged)):
			word, tag = tagged[index]
			pos_feature = {}
			pos_feature['l'] = index
			pos_feature['r'] = index
			pos_feature['val'] = tag
			pos_feature['t'] = 'pos'
			features[index].append(pos_feature)
		return

	def get_feature_gram(self, fragment, features):
		for l in xrange(len(fragment)):
			for n in xrange(1, self.settings.gram_length + 1):
				r = l + n
				if r > len(fragment):
					break
				gram_string = " ".join(fragment[l: r])
				# if gram_string in self.settings.all_grams:
				gram_feature = {}
				gram_feature['l'] = l
				gram_feature['r'] = r - 1 # We use inclusive intervals here
				gram_feature['val'] = gram_string
				gram_feature['t'] = 'gram'
				gram_feature['t+'] = '{}_gram'.format(n)
				features[l].append(gram_feature)
		return

	def get_feature_synset(self, ss, index):
		ss_feature = {}
		ss_feature['l'] = index
		ss_feature['r'] = index
		ss_feature['val'] = ss.offset()
		ss_feature['t'] = 'ss'
		return ss_feature

	def get_feature_wordnet(self, fragment, features):
		for index in xrange(len(fragment)):
			word = fragment[index]
			try:
				if features[index][0]['t'] == 'pos':
					pos = get_wordnet_pos(features[index][0]['val'])
				else:
					continue
			except KeyError:
				continue
			ss = lesk(fragment[index - self.settings.lesk_width: index + self.settings.lesk_width], word, pos=pos) # TODO: Apply smoothing
			if ss is None:
				continue
			ss_feature = self.get_feature_synset(ss, index)
			ss_feature['t+'] = 'self'
			ss_feature['w'] = self.settings.ss_weight['self'] # TODO: Apply smoothing
			features[index].append(ss_feature)
			
			hypernyms = ss.hypernyms()
			for hyper_ss in hypernyms:
				hyper_ss_feature = self.get_feature_synset(hyper_ss, index)
				hyper_ss_feature['t+'] = 'hyper'
				hyper_ss_feature['w'] = self.settings.ss_weight['hyper'] / len(hypernyms)
				features[index].append(hyper_ss_feature)

			similar_tos = ss.similar_tos()
			for similar_ss in similar_tos:
				similar_ss_feature = self.get_feature_synset(similar_ss, index)
				similar_ss_feature['t+'] = 'sim'
				similar_ss_feature['w'] = self.settings.ss_weight['sim'] / len(similar_tos)
				features[index].append(similar_ss_feature)

			also_sees = ss.also_sees()
			for also_ss in also_sees:
				also_ss_feature = self.get_feature_synset(also_ss, index)
				also_ss_feature['t+'] = 'also'
				also_ss_feature['w'] = self.settings.ss_weight['also'] / len(also_sees)
				features[index].append(also_ss_feature)
		return

	'''
	Featurizer extracts feature of text
	Each text contains a 
	'''
	def featurize(self, fragment):
		features = [[] for token in fragment]
		self.get_feature_pos(fragment, features)
		self.get_feature_gram(fragment, features)
		self.get_feature_wordnet(fragment, features)
		return features


# fragment = "your head look like a ball however hubert has a head \
# which is a polygon this difference derives from the fact that hubert is gamma perturbation stable"
# fragment = fragment.split(" ")


# all_grams = {}
# counter = 0
# for word in fragment:
# 	all_grams[word] = (counter, 0)
# 	counter += 1
# all_grams["your head"] = (counter, 0)
# counter += 1
# all_grams["a ball"] = (counter, 0)
# counter += 1
# all_grams["derives from"] = (counter, 0)
# counter += 1

# ss_weight = {
# 	'self': 1,
# 	'hyper': 0.1,
# 	'sim': 0.01,
# 	'also': 0.001
# }

# settings = Settings(all_grams, ss_weight)
# fea = Featurizer(settings)

# print fea.featurize(fragment)
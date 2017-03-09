from utils import default_gram_length
from utils import tag_ref_file, synset_ref_file, gram_ref_file
from helper import get_wordnet_info
from helper import get_pos_tags
from helper import get_wordnet_pos
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
# from pycorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP('http://localhost:9000')
# output = nlp.annotate(text, properties={
#   'annotators': 'tokenize,ssplit,pos,depparse,parse',
#   'outputFormat': 'json'
#   })

'''
Requirement:
	all grams: {string: True/data}
	We only need keys here
'''

class Settings():
	def __init__(self, ss_weight=None):
		if ss_weight is None:
			ss_weight = {
				'self': 1.,
				'hyper': 1.,
				'sim': 1.,
				'also': 1.
			}
		self.ss_weight = ss_weight 
		self.gram_length = default_gram_length
		self.lesk_width = 5

# Invalid vals are labelled by -1
class FeatureLabeler():
	def __init__(self):
		self.tag_to_label = {}
		self.label_to_tag = {}
		self.tag_offset = 0
		
		self.synset_to_label = {}
		self.label_to_synset = {}
		self.synset_offset = 0

		self.gram_to_label = {}
		self.label_to_gram = {}
		self.gram_offset = 0

		self.load_labels()

	def read_ref(self, file):
		from_label = {}
		to_label = {}
		with open(file, 'r') as f:
			for line in f:
				index = line.index(',')
				from_label[int(line[0:index])] = line[index + 1:].strip()
		for key in from_label:
			to_label[from_label[key]] = key
		return from_label, to_label

	def load_labels(self, tag_file=None, synset_file=None, gram_file=None):
		if tag_file is None:
			tag_file = tag_ref_file
		if synset_file is None:
			synset_file = synset_ref_file
		if gram_file is None:
			gram_file = gram_ref_file

		self.label_to_tag, self.tag_to_label = self.read_ref(tag_file)
		self.label_to_synset, self.synset_to_label = self.read_ref(synset_file)
		self.label_to_gram, self.gram_to_label = self.read_ref(gram_file)
		
		self.gram_offset = 1 # GLOVE coocc is 1 indexed
		self.synset_offset = self.gram_offset + len(self.label_to_gram)
		self.tag_offset = self.synset_offset + len(self.label_to_synset)

		self.minimum = 1
		self.maximum = self.tag_offset + len(self.label_to_tag)
		print "labeler loaded {} labels".format(self.maximum - self.minimum)
		return

	def tag_val(self, tag):
		try:
			return self.tag_to_label[tag] + self.tag_offset
		except KeyError:
			return -1

	def synset_val(self, ss_offset):
		try:
			return self.synset_to_label[str(ss_offset)] + self.synset_offset
		except KeyError:
			return -1

	def gram_val(self, gram_string):
		try:
			return self.gram_to_label[gram_string] + self.gram_offset
		except KeyError:
			return -1

	def val_to_feature(self, val):
		if val < self.minimum or val >= self.maximum:
			return None, None
		elif val < self.synset_offset:
			return self.label_to_gram[val - self.gram_offset], 'gram'
		elif val < self.tag_offset:
			return self.label_to_synset[val - self.synset_offset], 'ss'
		else:
			return self.label_to_tag[val - self.tag_offset], 'pos'

	def generate_vocab_file(self, path):
		print "writing vocabulary to {}".format(path)
		f = open(path, 'w')
		for val in xrange(self.minimum, self.maximum):
			description, fea_type = self.val_to_feature(val)
			if fea_type == 'gram':
				f.write('{} 1\n'.format(description.replace(' ', '_')))
			if fea_type == 'ss':
				f.write('ss_{} 1\n'.format(description))
			if fea_type == 'pos':
				f.write('pos_{} 1\n'.format(description))
		f.close()

class Featurizer():
	def __init__(self, settings=None, labeler=None):
		if settings is None:
			settings = Settings()
		if labeler is None:
			labeler = FeatureLabeler()
		self.settings = settings
		self.labeler = labeler

	def get_feature_pos(self, fragment, features):
		tagged = pos_tag(fragment)
		for index in xrange(len(tagged)):
			word, tag = tagged[index]
			pos_feature = {}
			pos_feature['l'] = index
			pos_feature['r'] = index
			pos_feature['val'] = self.labeler.tag_val(tag)
			pos_feature['tagval'] = tag
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
				val = self.labeler.gram_val(gram_string)
				if val != -1:
					gram_feature = {}
					gram_feature['l'] = l
					gram_feature['r'] = r - 1 # We use inclusive intervals here
					gram_feature['val'] = val
					gram_feature['t'] = 'gram'
					gram_feature['t+'] = '{}_gram'.format(n)
					features[l].append(gram_feature)
		return

	def get_feature_synset(self, ss, index):
		ss_feature = {}
		ss_feature['l'] = index
		ss_feature['r'] = index
		ss_feature['val'] = self.labeler.synset_val(ss.offset())
		ss_feature['t'] = 'ss'
		return ss_feature

	def get_feature_wordnet(self, fragment, features):
		for index in xrange(len(fragment)):
			word = fragment[index]
			try:
				if features[index][0]['t'] == 'pos':
					pos = get_wordnet_pos(features[index][0]['tagval'])
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
		# print "featurize"
		return features


# fragment = "your head look like a ball however hubert has a head \
# which is a polygon this difference derives from the fact that hubert is gamma perturbation stable"
# fragment = fragment.split(" ")


# settings = Settings() # all_grams, ss_weight])
# fea = Featurizer(settings)

# print fea.featurize(fragment)

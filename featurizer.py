from utils import default_gram_length
from utils import tag_ref_file, synset_ref_file, gram_ref_file #, ner_ref_file
from helper import get_wordnet_info
from helper import get_pos_tags
from helper import get_wordnet_pos
from nltk import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
# import spacy                         # See "Installing spaCy"
from pycorenlp import StanfordCoreNLP
import random
# we only need tagger and entity
# def custom_pipeline(nlp):
    # return  # (nlp.tagger) #, nlp.entity)



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

	def load_labels(self, tag_file=None, synset_file=None, gram_file=None):#, ner_file=None):
		if tag_file is None:
			tag_file = tag_ref_file
		if synset_file is None:
			synset_file = synset_ref_file
		if gram_file is None:
			gram_file = gram_ref_file
		# if ner_file is None:
		# 	ner_file = ner_ref_file

		self.label_to_tag, self.tag_to_label = self.read_ref(tag_file)
		self.label_to_synset, self.synset_to_label = self.read_ref(synset_file)
		self.label_to_gram, self.gram_to_label = self.read_ref(gram_file)
		# self.label_to_ner, self.ner_to_label = self.read_ref(ner_file)
		
		self.gram_offset = 1 # GLOVE cooc is 1 indexed
		self.synset_offset = self.gram_offset + len(self.label_to_gram)
		self.tag_offset = self.synset_offset + len(self.label_to_synset)
		# self.ner_offset = self.tag_offset + len(self.label_to_tag)

		self.minimum = 1
		self.maximum = self.tag_offset
		# self.maximum = self.ner_offset + len(self.label_to_ner)
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

	# def ner_val(self, ner_string):
	# 	try:
	# 		return self.ner_to_label[ner_string] + self.ner_offset
	# 	except KeyError:
	# 		print "ner error"
	# 		return -1

	def val_to_feature(self, val):
		if val < self.minimum:
			return None, None
		elif val < self.synset_offset:
			return self.label_to_gram[val - self.gram_offset], 'gram'
		elif val < self.tag_offset:
			return self.label_to_synset[val - self.synset_offset], 'ss'
		elif val < self.maximum:
			return self.label_to_tag[val - self.tag_offset], 'pos'
		# elif val < self.maximum:
		# 	return self.label_to_ner[val - self.ner_offset], 'ner'

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
			# if fea_type == 'ner':
			# 	f.write('ner_{} 1\n'.format(description))
		f.close()

class Featurizer():
	def __init__(self, settings=None, labeler=None):
		if settings is None:
			settings = Settings()
		if labeler is None:
			labeler = FeatureLabeler()
		self.settings = settings
		self.labeler = labeler
		self.nlp = StanfordCoreNLP('http://localhost:9000')
		#  self.nlp = spacy.load('en')               # You are here.

	def get_feature_pos(self, fragment, tagged, features):	
		for index in xrange(len(tagged)):
			tag = tagged[index]
			pos_feature = {}
			pos_feature['l'] = index
			pos_feature['r'] = index
			pos_feature['val'] = self.labeler.tag_val(tag)
			pos_feature['tagval'] = tag
			pos_feature['t'] = 'pos'
			features[index].append(pos_feature)
		return

	def get_feature_ner(self, fragment, tagged, features):
		for index in xrange(len(tagged)):
			tag = tagged[index]
			if tag == 'O':
				return
			pos_feature = {}
			pos_feature['l'] = index
			pos_feature['r'] = index
			pos_feature['val'] = self.labeler.tag_val(tag)
			pos_feature['t'] = 'ner'
			features[index].append(pos_feature)
		return

	def get_feature_gram(self, fragment, features):
		for l in xrange(len(fragment)):
			for n in xrange(1, self.settings.gram_length + 1):
				r = l + n
				if r > len(fragment):
					break
				gram_string = " ".join(fragment[l: r]).lower()
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

			# we restrict number of other synsets to be three
			# hypernyms = ss.hypernyms()
			# if len(hypernyms) > 0:
			# 	hyper_ss = hypernyms[random.randint(0, len(hypernyms) - 1)]
			# 	hyper_ss_feature = self.get_feature_synset(hyper_ss, index)
			# 	hyper_ss_feature['t+'] = 'hyper'
			# 	features[index].append(hyper_ss_feature)
			# 	continue

			# similar_tos = ss.similar_tos()
			# if len(similar_tos) > 0:
			# 	similar_ss = similar_tos[random.randint(0, len(similar_tos) -1 )]
			# 	similar_ss_feature = self.get_feature_synset(similar_ss, index)
			# 	similar_ss_feature['t+'] = 'sim'
			# 	features[index].append(similar_ss_feature)
			# 	continue

			# also_sees = ss.also_sees()
			# if len(also_sees) > 0:
			# 	also_ss = also_sees[random.randint(0, len(also_sees) - 1)]
			# 	also_ss_feature = self.get_feature_synset(also_ss, index)
			# 	also_ss_feature['t+'] = 'also'
			# 	features[index].append(also_ss_feature)
			# 	continue
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
	def featurize(self, text):

		output = self.nlp.annotate(text, properties={
		  'annotators': 'tokenize, ssplit, pos', # , ', #, lemma', # ,ner,, ner',
		  # 'annotators': 'tokenize,ssplit,pos,lemma,ner',
		  'outputFormat': 'json'
		})
		fragment = []
		pos = []
		# ner = []
		# lemma = []
		for sentence in output['sentences']:
			for token in sentence['tokens']:
				fragment.append(token['word'])
				pos.append(token['pos'])
		features = [[] for token in fragment]
		self.get_feature_pos(fragment, pos, features)
		self.get_feature_gram(fragment, features)
		self.get_feature_wordnet(fragment, features)
		# self.get_feature_ner(fragment, ner, features)
		return features

		# for w in doc:
		# 	fragment.append(w.text)
		# 	pos.append(w.tag_)
		# 	ner.append(w.ent_type_)
		# 	lemma.append(w.lemma_)
		# doc = self.nlp(text) # See "Using the pipeline"
		# fragment = []
		# features = [[] for w in doc]
		# pos = []
		# ner = []
		# lemma = []
			
		# self.get_feature_pos(fragment, pos, features)
		# self.get_feature_gram(fragment, features)
		# # self.get_feature_ner(fragment, ner, features)
		# return features
		# return []
		# # 
		
		# This is extremely slow
		# 
		# print "featurize"
		# for sentence in output['sentences']:
		# 	for token in sentence['tokens']:
		# 		fragment.append(token['word'])
		# 		pos.append(token['pos'])
		# print output
		# exit(-1)
		# for token in output['tokens']:
		# 	fragment.append(token['word'])
		# 	pos.append(token['pos'])
				# lemma.append(token['lemma'])
		# print "length of fragment", len(fragment)
		

# fragment = "your head look like a ball however hubert has a head \
# which is a polygon this difference derives from the fact that hubert is gamma perturbation stable"
# fragment = fragment.split(" ")


# settings = Settings() # all_grams, ss_weight])
# fea = Featurizer(settings)

# print fea.featurize(fragment)

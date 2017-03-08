from nltk.corpus import wordnet as wn
# from nltk.wsd import lesk
from nltk.stem.snowball import SnowballStemmer
import sys
import os
import nltk
print(nltk.pos_tag('What is the airspeed of an unladen swallow ?'.split()))

exit(0)

counter = 0
for ss in list(wn.all_synsets('v')):
	if len(ss.entailments()) != 0:
		print ss
		print ss.entailments()
		counter += 1
		if counter > 3:
			exit(0)
	
print "No entailments in ", counter

from nltk.corpus import wordnet as wn

# def is_noun(tag):
#     return tag in ['NN', 'NNS', 'NNP', 'NNPS']


# def is_verb(tag):
#     return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


# def is_adverb(tag):
#     return tag in ['RB', 'RBR', 'RBS']


# def is_adjective(tag):
#     return tag in ['JJ', 'JJR', 'JJS']


# def penn_to_wn(tag):
#     if is_adjective(tag):
#         return wn.ADJ
#     elif is_noun(tag):
#         return wn.NOUN
#     elif is_adverb(tag):
#         return wn.ADV
#     elif is_verb(tag):
#         return wn.VERB
#     return None

def lesk(context_sentence, ambiguous_word, pos=None, synsets=None):
    """Return a synset for an ambiguous word in a context.

    :param iter context_sentence: The context sentence where the ambiguous word
    occurs, passed as an iterable of words.
    :param str ambiguous_word: The ambiguous word that requires WSD.
    :param str pos: A specified Part-of-Speech (POS).
    :param iter synsets: Possible synsets of the ambiguous word.
    :return: ``lesk_sense`` The Synset() object with the highest signature overlaps.

    This function is an implementation of the original Lesk algorithm (1986) [1].

    Usage example::

        >>> lesk(['I', 'went', 'to', 'the', 'bank', 'to', 'deposit', 'money', '.'], 'bank', 'n')
        Synset('savings_bank.n.02')

    [1] Lesk, Michael. "Automatic sense disambiguation using machine
    readable dictionaries: how to tell a pine cone from an ice cream
    cone." Proceedings of the 5th Annual International Conference on
    Systems Documentation. ACM, 1986.
    http://dl.acm.org/citation.cfm?id=318728
    """

    context = set(context_sentence)
    if synsets is None:
        synsets = wn.synsets(ambiguous_word)

    if pos:
        synsets = [ss for ss in synsets if str(ss.pos()) == pos]

    if not synsets:
        return None

    _, sense = max(
        (len(context.intersection(ss.definition().split())), ss) for ss in synsets
    )

    return sense

# >>> dog = wn.synset('dog.n.01')
# >>> dog.hypernyms()
# [Synset('canine.n.02'), Synset('domestic_animal.n.01')]
# >>> dog.hyponyms()  # doctest: +ELLIPSIS
# [Synset('basenji.n.01'), Synset('corgi.n.01'), Synset('cur.n.01'), Synset('dalmatian.n.02'), ...]
# >>> dog.member_holonyms()
# [Synset('canis.n.01'), Synset('pack.n.06')]
# >>> dog.root_hypernyms()
# [Synset('entity.n.01')]
# >>> wn.synset('dog.n.01').lowest_common_hypernyms(wn.synset('cat.n.01'))
# [Synset('carnivore.n.01')]

# with open('data/debug/100sents.sent', 'r') as f:
# 	sentences = f.readlines()
st = SnowballStemmer('english')
	# for sentence in sentences:
	# 	for word in sentence.split(' '):
# 		
# for sent_index in xrange(5, len(sentences), 10):
sent_index = 20
# word_index = 14
# try:
# 	if sys.argv[1] is not None:
# 		sent_index = int(sys.argv[1])
# 	if sys.argv[2] is not None:
# 		word_index = int(sys.argv[2])
# except IndexError:
# 	pass
# sentence = sentences[sent_index]
# print sentence
# words = sentence.split(' ')
#	for word_index in xrange(0, len(words), 5):
# word = words[word_index]
word = sys.argv[1]
ss = lesk([word], word)
print word, st.stem(word)
print wn.synsets(word)
print ss
if ss is not None:
	print "pos", ss.pos()
	print "hyper", ss.hypernyms()
	print "instance_hyper", ss.instance_hypernyms()
	print "instance_hypo", ss.instance_hyponyms()
	print "similar_to", ss.similar_tos()
	print "attributes", ss.attributes()
	print "also_sees", ss.also_sees()
	print "entailments", ss.entailments()

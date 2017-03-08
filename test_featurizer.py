from helper import get_wordnet_info, get_pos_tags
sentence = 'cat wildcat cat sits on a mat and says that Stanford is a cool place'
index = 0
context = sentence.split()
tags = get_pos_tags(context)
Dict = get_wordnet_info(index, context, tags)

import nltk

sentence = 'cat wildcat cat sits on a mat and says that Stanford is a cool place'
context = sentence.split()
tags = get_pos_tags(context)
print tags
print context[0]
print get_wordnet_info(0, context, tags)

# TODO
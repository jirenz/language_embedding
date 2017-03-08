# http://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk
from nltk.data import load
tagdict = load('help/tagsets/upenn_tagset.pickle')
print tagdict.keys()
# ['PRP$', 'VBG', 'VBD', '``', 'VBN', ',', "''", 'VBP', 'WDT', ...
with open('treebank_tags_table.ref', 'w') as f:
	for index, tag in enumerate(tagdict.keys()):
		f.write('{},{}\n'.format(index, tag))

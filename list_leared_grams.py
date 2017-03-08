import sys
import json

vocab_f = open('data/glove_mar6/vocab.txt', 'r')
label_gram_f = open('data/glove_mar6/label_gram.json', 'r')
label_gram = json.load(label_gram_f)
print "label gram length", len(label_gram)
# gram_label_f = open('data/glove_mar6/gram_label.json', 'r')
# gram_label = json.load(gram_label_f)
output_vocab_f = open('data/glove_mar6/translated_vocab.txt', 'w')
frequent_gram_f = open('data/glove_mar6/top_grams.txt', 'w')
for line in vocab_f:
	label, count = line.strip().split(' ')
	output_vocab_f.write('{}, {}\n'.format(label_gram[label], count))
	frequent_gram_f.write('{}\n'.format(label_gram[label]))
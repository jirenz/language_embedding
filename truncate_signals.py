import sys
import argparse


def read_file(f):
	grams = []
	synsets = []
	tags = []
	for line in f:
		if line.startswith("#"):
			continue
		if line.startswith("--grams"):
			cur = grams
			continue
		if line.startswith("--synsets"):
			cur = synsets
			continue
		if line.startswith("--tags"):
			cur = tags
			continue
		line = line.rstrip('\n')
		text = line[:line.rfind(' ')].strip()
		count = float(line[line.rfind(' '):].strip())
		# if (text.find(' the') >= 0 or text.find('the ') >= 0 or text.find(' a') >= 0 or text.find('a ') != 'a' or (text.find(' an ') >= 0 and text != 'an'):
		# 	continue
		# 	This is broken
		cur.append((text, count))
	grams.reverse()
	synsets.reverse()
	tags.reverse()
	return grams, synsets, tags

def filter_n_grams(grams):
	words = []
	n_grams = []
	for gram in grams:
		token, count = gram
		token = token.strip()
		if token.find(' ') >= 0:
			n_grams.append((token, count))
		else:
			words.append((token, count))
	return words, n_grams

def dump_ref(f, arr, count, offset = 0):
	for index in xrange(count):
		token, _ = arr[index]
		f.write('{},{}\n'.format(index + offset, token))




parser = argparse.ArgumentParser(description='For given wikipedia featured cooc, reduce and shuffle them')
parser.add_argument('inputfile', metavar='inputfile', type=str, help='fcount file to be processed')
parser.add_argument('outputpath', metavar='outputpath', type=str, help='the path to output ref file')
parser.add_argument('--num_words', metavar='num_words', type=int, default=60000)
parser.add_argument('--num_grams', metavar='num_words', type=int, default=20000)
parser.add_argument('--num_synsets', metavar='num_words', type=int, default=20000)
parser.add_argument('--num_tags', metavar='num_words', type=int, default=100)


# parser.add_argument('-s', '--seed', default=12345, help='random seed')
args = parser.parse_args()
print args

num_words = args.num_words
num_grams = args.num_grams
num_synsets = args.num_synsets
num_tags = args.num_tags

f = open(args.inputfile, 'r')
out_path = args.outputpath

grams, synsets, tags = read_file(f)
sample1, sample1_count = grams[0]
sample2, sample2_count = grams[1]
assert sample1_count > sample2_count

# words, grams = filter_n_grams(grams)

# num_words = min(len(words), num_words)
num_grams = min(len(grams), num_grams)
num_synsets = min(len(synsets), num_synsets)
num_tags = min(len(tags), num_tags)

# print "words:", num_words
print "grams:", num_grams
print "synsets:", num_synsets
print "tags:", num_tags

with open(out_path + 'n_gram_table.ref', 'w') as f_out:
	# dump_ref(f_out, words, num_words)
	# dump_ref(f_out, grams, num_grams, offset=num_words)
	dump_ref(f_out, grams, num_grams, offset=num_words)

with open(out_path + 'synset_offset_table.ref', 'w') as f_out:
	dump_ref(f_out, synsets, num_synsets)

with open(out_path + 'treebank_tag_table.ref', 'w') as f_out:
	dump_ref(f_out, tags, num_tags)
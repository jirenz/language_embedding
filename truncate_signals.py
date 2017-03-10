import sys

num_grams = 60000
num_synsets = 20000
num_tags = 100

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

def dump_ref(f, arr, count):
	for index in xrange(count):
		token, _ = arr[index]
		f.write('{},{}\n'.format(index, token))


f = open(sys.argv[1], 'r')
out_path = sys.argv[2]

grams, synsets, tags = read_file(f)
sample1, sample1_count = grams[0]
sample2, sample2_count = grams[1]
assert sample1_count > sample2_count

num_grams = min(len(grams), num_grams)
num_synsets = min(len(synsets), num_synsets)
num_tags = min(len(tags), num_tags)

print "grams:", num_grams
print "synsets:", num_synsets
print "tags:", num_tags

with open(out_path + 'n_gram_table.ref', 'w') as f_out:
	dump_ref(f_out, grams, num_grams)

with open(out_path + 'synset_offset_table.ref', 'w') as f_out:
	dump_ref(f_out, synsets, num_synsets)

with open(out_path + 'treebank_tag_table.ref', 'w') as f_out:
	dump_ref(f_out, tags, num_tags)
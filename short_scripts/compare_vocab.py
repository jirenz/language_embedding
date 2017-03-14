import sys
def read_vocab(file):
	out = {}
	with open(file, 'r') as f:
		for line in f:
			out[line.strip()] = True
	return out

file_1 = sys.argv[1]
file_2 = sys.argv[2]

vocab_1 = read_vocab(sys.argv[1])
vocab_2 = read_vocab(sys.argv[2])

vocab_1_unique = []
vocab_2_unique = []
intersect = []
for key in vocab_1:
	if key in vocab_2:
		intersect.append(key)
	else:
		vocab_1_unique.append(key)
for key in vocab_2:
	if key not in vocab_1:
		vocab_2_unique.append(key)


print "lenth:", file_1, len(vocab_1)
print "lenth:", file_2, len(vocab_2)
print "intersect", len(intersect)
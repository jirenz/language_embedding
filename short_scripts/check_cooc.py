import sys
from struct import Struct
import os

'''
typedef double real;

typedef struct cooccur_rec {
	int word1;
	int word2;
	real val;
} CREC;
'''

CREC_FORMAT = 'iid'

def read_vocab_file(filename):
	vocab = {}
	ivocab = {}
	counter = 0
	with open(filename, 'r') as f:
		for line in f:
			word = line.strip().split(' ')[0]
			vocab[word] = counter
			ivocab[counter] = word
			counter += 1
	return vocab, ivocab

def read_CREC(binary_stream):
	crec = Struct(CREC_FORMAT)
	buf = binary_stream.read(crec.size)
	if len(buf) != crec.size:
		raise ValueError
	return crec.unpack_from(buf)

def write_CREC(binary_stream, word1, word2, val):
	crec = Struct(CREC_FORMAT)
	try:
		return binary_stream.write(crec.pack(word1, word2, val))
	except: 
		print word1, word2, val
		raise

base_file = sys.argv[1]
vocab_base = sys.argv[2]
bvocab, bivocab = read_vocab_file(vocab_base)
check_file = sys.argv[3]
vocab_check = sys.argv[4]
cvocab, civocab = read_vocab_file(vocab_check)
base_cooc = {}

translate = {}
for key in civocab:
	translate[key] = bvocab[civocab[key]]
print "vocab file length", len(bvocab), len(cvocab)
print "finish reading vocab, start to read base file"


with open(base_file, 'rb') as f:
	while True:
		try:
			word1, word2, val = read_CREC(f)
			base_cooc[(word1, word2)] = val
		except ValueError:
			break
print "base file size", len(base_cooc)
correct = 0
not_found = 0
wrong = 0
close = 0
print "starting to read check file"
with open(check_file, 'rb') as f:
	while True:
		try:
			word1, word2, val = read_CREC(f)
			word1 = translate[word1]
			word2 = translate[word2]
			if (word1, word2) not in base_cooc:
				not_found += 1
				continue
			old_val = base_cooc[(word1, word2)]
			if val == old_val:
				correct += 1
			elif abs(val - old_val) / abs(old_val) < 0.1:
				close += 1
			else:
				wrong += 1
		except ValueError:
			break
		except KeyError:
			continue
print "total:", correct + not_found + wrong + close
print "correct:", correct
print "not found:", not_found
print "wrong", wrong
print "close", close
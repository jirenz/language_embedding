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


def read_CREC(binary_stream):
	crec = Struct(CREC_FORMAT)
	buf = binary_stream.read(crec.size)
	if len(buf) != crec.size:
		raise ValueError
	return crec.unpack_from(buf)

def write_CREC(binary_stream, word1, word2, val):
	crec = Struct(CREC_FORMAT)
	return binary_stream.write(crec.pack(wrod1, word2, val))
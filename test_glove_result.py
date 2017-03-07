# This code tests the result of vectors trained by GloVe

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import 

parser.add_argument('-i', '--inputfile', default='./data/glove_mar6/vectors.txt', type=str, help='input file')
parser.add_argument('-l', '--labelgram', default='./Tokenized/label_gram.json', type=str, help='output file')
args = parser.parse_args()
print(args)

inputfile = args.inputfile;
labelgram = args.labelgram;

Dict = {}



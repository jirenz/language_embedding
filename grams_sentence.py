import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import sanitize_line
from helper import filter_with_alphabet
from nltk import sent_tokenize

parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate a file where each line is a sentence')
parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
					help='files to be processed')
parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz -',
	 type=str, help='supported alphabet')

# Macros and Constants
args = parser.parse_args()
print(args)

print len(args.inputfiles), "files found."

def split_into_sentences(text):
	lines = sent_tokenize(text)
	return [filter_with_alphabet(line, args.alphabet) for line in lines]

Counter = 0 # Number of articles processed
file_count = 0
for inputfile in args.inputfiles:
	print "Processing file:", inputfile
	F_in = open(inputfile, "r")
	file_name, _ = splitext(basename(inputfile))
	F_out = open(args.outputpath + file_name + ".sent", "w")
	text = ""
	# All articles begin with '<doc' and end with '</doc>'
	for line in F_in:
		if line.startswith("<doc"):
			continue
		if line.startswith("</doc>"):
			# some paragraph ends
			sentences = split_into_sentences(text)
			for sentence in sentences:
				F_out.write(sentence)
				F_out.write('\n')
			text = ""
			# 
			Counter += 1
			if Counter % 100 == 0:
				print "Finished processing article:", Counter
			continue
		text += sanitize_line(line)
		# cast to unicode string, to lower case, remove non-alphabet characters before processing
	F_in.close()
	F_out.close()
			
	#dump the gram info	
	print "Finish Processing File " + file_name
	file_count += 1
# End Processing files

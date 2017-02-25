"""
ngram-stats.py :	For given wikipedia dump files (preprocessed by WikiExtractor),
					output the most frequent n-grams for n in [2, k], where k is
					given in input (k = 2 by default).

Usage :	python ngram-stats.py [-k value-of-k] input-directory
"""
# Macros and Constants
alphabets = "abcdefghijklmnopqrstuvwxyz " # alphabets plus space # TODO: @punctuations
meaningful_rate = 0.1 # only keep this percent of grams each iteration
skipfile_rate = 0.7 # when there are too many files, instead of only learn on a prefix, we should randomly sample files
threshold = 0.1 # TODO: up to change
outputdir = "/media/pear/Storage/CS224N-tmpwork/"
	
import sys
import json
from os import listdir
from os.path import isfile, join
import random

def smoothone(x): # make those close to 1 closer
	return 1 - (1 - x) ** 2
	
# Begin Preprocess system arguments
k = 2
args = sys.argv
if (args[1] == '-k'):
	k = int(args[2])
	mypath = args[3]
else:
	mypath = args[1]
mypath = outputdir + mypath
print "Process files in directory " + mypath + " with k =", k
# End Preprocess system arguments

# Begin Extract List of files
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
files.sort()
print len(files), "files found."
# End Extract List of files

# Add each n-gram (n = gram_length) from texts, into Dict
def add_to_dict(Dict, text, gram_length, debug = False):
	text_length = len(text)
	for i in range(text_length + 1 - gram_length):
		gram = unicode(" ".join(text[i : i + gram_length]))
		if debug: print i, gram
		try:
			Dict[gram] += 1
		except KeyError:
			Dict[gram] = 1
			
# Sort Dict CMP
def weight(a):
	return (a[1] ** smoothone(a[2])) * (2 ** a[3])
def cmp_1(a,b):
	if weight(a) > weight(b): # compare likelihood
		return -1
	else:
		return 1

# remove non-ascii
def remove_nonascii(text):
	return str(''.join([i if ord(i) < 128 else "" for i in text]))
	
# Begin Processing files
Dict = {} # Dict is a n-gram dictionary
Word_Dict = {} # Word_Dict works for single word counting only
Counter = 0 # Number of articles processed

for file_name in files:
	# load result from last iteration (last file)
	try:
		F = open(outputdir + "training/result.txt", "r")
		Dict = json.load(F)
	except IOError:
		Dict = {}	
	try:
		F = open(outputdir + "training/word-freq.txt", "r")
		Word_Dict = json.load(F)
	except IOError:
		Word_Dict = {}
	
	file_path = mypath + "/" + file_name
	with open(file_path, "r") as F:
		lines = F.readlines()
	text = []
	# All articles begin with '<doc' and end with '</doc>'
	for line in lines:
		if line.startswith("<doc"):
			pass
		else:
			if line.startswith("</doc>"):
				# some paragraph ends
				if random.random() < skipfile_rate: 
					del text[:] # **
					continue # with probability skipfile_rate, we will skip the current file
				Counter += 1
				print "Going to process article", Counter, "; this article has", len(text), "words."
				add_to_dict(Word_Dict, text, 1)
				for gram_length in range(2, k + 1): # also need single-word appearance
					add_to_dict(Dict, text, gram_length)
				del text[:] # **
				print "Finished processing article", Counter
			else:
				# cast to unicode string, to lower case, remove non-alphabet characters before processing
				line = remove_nonascii(line).lower()
				text.extend(''.join(c for c in line if c in alphabets).split()) 
	
	print "Finish adding dictionary."
	sorted_Dict = [] # sort by weight()
	for gram in Dict:
		gram_time = Dict[gram]
		words = gram.split(" ")
		if len(words) > 1:
			# not a single word
			min_word_time = Word_Dict[words[0]]
			for word in words:
				min_word_time = min(min_word_time, Word_Dict[word])
			rate = (gram_time * 1.0) / min_word_time
			if (rate > threshold):
				sorted_Dict.append((gram, gram_time, rate, len(words)))
	print "Sorting Dictionary of size", len(sorted_Dict)
	sorted_Dict = sorted(sorted_Dict, cmp = cmp_1)
	
	with open(outputdir + "training/rate_result.txt", "w") as F:
		F.write(json.dumps(sorted_Dict))

	# Add back to a Dict and save it to file, for next iteration
	total_grams = len(sorted_Dict)	
	meaningful_Dict = {}
	breaker = 0 # only keep the first several
	for triple in sorted_Dict: #slice a prefix depend on testing result
		meaningful_Dict[triple[0]] = triple[1]
		breaker += 1
		if breaker >= total_grams * meaningful_rate: break
	
	with open(outputdir + "training/result.txt", "w") as F:
		F.write(json.dumps(meaningful_Dict))
	with open(outputdir + "training/word-freq.txt", "w") as F:
		F.write(json.dumps(Word_Dict))
	
	print "Finish Processing File " + file_name
	
	# clear up
	Dict.clear()
	meaningful_Dict.clear()
	Word_Dict.clear()
	del sorted_Dict[:]
# End Processing files




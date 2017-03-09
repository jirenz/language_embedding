import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from nltk import word_tokenize
from multiprocessing import Process
from featurizer import Featurizer, Settings
from nltk import word_tokenize
from helper import filter_with_alphabet
from helper import sanitize_line
from helper import write_checkpoint_file
from helper import interval_intersect
import coocformatter

def inc_coocurrence(Dict, label_1, label_2, value):
	if label_1 < 0 or label_2 < 0:
		return
	if label_1 > label_2: label_1, label_2 = label_2, label_1
	try:
		Dict[(label_1, label_2)] += value
	except KeyError:
		Dict[(label_1, label_2)] = value

def process(text, featurizer, cooc, window_size):
	features = featurizer.featurize(text)
	N = len(features)
	for center in range(window_size, N):
		# only consider left half, notice that the result matrix is upper-right only
		cur_list = features[center]
		for l in range(center - window_size, center):
			l_list = features[l]
			for token_1 in cur_list:
				for token_2 in l_list:
					if not interval_intersect(token_1["l"], token_1["r"], token_2["l"], token_2["r"]):
						inc_coocurrence(cooc, token_1["val"], token_2["val"], token_1.get("w", 1.) * token_2.get("w", 1.) / (center - l))
	return N

def dump_to_file(worker_id, cooc, F_out):
	sys.stdout.write("{}: Dumping {} entries\n".format(worker_id, len(cooc)))
	for key, val in cooc.iteritems():
		word1, word2 = key
		coocformatter.write_CREC(F_out, word1, word2, val)
	return

def worker_task(files, args, worker_id):
	featurizer = Featurizer(Settings())
	cooc = {} # in format (word1, word2) : count
	Counter = 0 # Number of articles processed
	file_count = 0
	text = []
	for inputfile in files:
		tokens_count = 0
		file_name, _ = splitext(basename(inputfile))
		F_out = open(join(args.outputpath, file_name + ".cooc_chunked"), 'wb')
		sys.stdout.write("{}: Processing file:{}\n".format(worker_id, inputfile))
		with open(inputfile, "r") as F:
			text = []
			# All articles begin with '<doc' and end with '</doc>'
			for line in F:
				if line.startswith("<doc"):
					continue
				if line.startswith("</doc>"):
					# some paragraph ends
					tokens_count += process(" ".join(text), featurizer, cooc, args.window_size)
					text = []
					Counter += 1
					if Counter%200 == 0:
						dump_to_file(worker_id, cooc, F_out)
						cooc = {}
					if Counter % 5000 == 0:
						sys.stdout.write("{}: Finished processing article:{}\n".format(worker_id, Counter))
					continue
				text.append(line)
		dump_to_file(worker_id, cooc, F_out)
		cooc = {}
		F_out.close()
		sys.stdout.write("{}: Finished processing file:{}: {} tokens, {} entries found\n".format(worker_id, inputfile, tokens_count, len(cooc)))
		file_count += 1
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For a given wiki corpus, generate features for it')
	parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
						help='files to be processed')
	parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
	parser.add_argument('--cores', default=1, type=int, help='number of concurrent threads')
	parser.add_argument('--window_size', default=6, type=int, help='window size for cooccurrence')
	parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz -',
		 type=str, help='supported alphabet')
	args = parser.parse_args()
	print args
	print len(args.inputfiles), "files found."

	workers = []

	files_per_worker = int(len(args.inputfiles) / (1. * args.cores)) + 1
	sys.stdout.write("{} files per worker\n".format(files_per_worker))
	for i in range(0, len(args.inputfiles), files_per_worker):
		end = i + files_per_worker
		if end > len(args.inputfiles):
			end = len(args.inputfiles)
		files_for_worker = args.inputfiles[i:end]
		p = Process(target=worker_task, args=(files_for_worker, args, i / files_per_worker))
		p.start()
		workers.append(p)
	for idx, worker in enumerate(workers):
		worker.join()
		sys.stdout.write("{}: Exited with code {}\n".format(idx, worker.exitcode))
		if worker.exitcode != 0:
			exit(1)

	write_checkpoint_file(args.outputpath)
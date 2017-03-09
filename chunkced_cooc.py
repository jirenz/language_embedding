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
import coocformatter

def process(text, featurizer, cooc):
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
	return


def worker_task(files, args, worker_id):
	featurizer = Featurizer(Settings())
	cooc = {} # in format (word1, word2) : count
	Counter = 0 # Number of articles processed
	file_count = 0
	text = []
	for inputfile in files:
		sys.stdout.write("{}: Processing file:{}\n".format(worker_id, inputfile))
		dic = {}
		with open(inputfile, "r") as F:
			text = []
			# All articles begin with '<doc' and end with '</doc>'
			for line in F:
				if line.startswith("<doc"):
					continue
				if line.startswith("</doc>"):
					# some paragraph ends
					process(text, featurizer, cooc)
					text = []
					Counter += 1
					if Counter % 5000 == 0:
						sys.stdout.write("{}: Finished processing article:{}\n".format(worker_id, Counter))
					continue
				text.extend(word_tokenize(filter_with_alphabet(sanitize_line(line), args.alphabet)))
		file_name, _ = splitext(basename(inputfile))
		with open(join(args.outputpath, file_name + ".cooc_chunked"), 'wb') as F:
			for key, val in cooc.iteritems():
				word1, word2 = key
				coocformatter.write_CREC(F, word1, word2, key)

		sys.stdout.write("{}: Finished processing file:{}\n".format(worker_id, inputfile))
		file_count += 1
		# clear up
		del dic
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For a given wiki corpus, generate features for it')
	parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
						help='files to be processed')
	parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
	parser.add_argument('--cores', default=6, type=int, help='number of concurrent threads')
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
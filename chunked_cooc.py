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
from helper import inc_coocurrence
from helper import process_features
from helper import dump_cooc_to_file
import coocformatter




def worker_task(files, args, worker_id):
	featurizer = Featurizer()
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
			chars = 0
			# All articles begin with '<doc' and end with '</doc>'
			for line in F:
				if line.startswith("<doc"):
					continue
				if line.startswith("</doc>"):
					# some paragraph ends
					tokens_count += process(" ".join(text), featurizer, cooc, args.window_size)
					text = []
					chars = 0
					Counter += 1
					if Counter % 500 == 0:
						sys.stdout.write("{}: Finished processing article:{}\n".format(worker_id, Counter))
						dump_cooc_to_file(worker_id, cooc, F_out)
						cooc = {}
					continue
				text.append(line) # Cannot be longer than 100000
				chars += len(line)
				if chars > 10000:
					tokens_count += process_features(" ".join(text), featurizer, cooc, args.window_size)
					text = []
					chars = 0
		dump_cooc_to_file(worker_id, cooc, F_out)
		cooc = {}
		F_out.close()
		sys.stdout.write("{}: Finished processing file:{}: {} tokens\n".format(worker_id, inputfile, tokens_count))
		file_count += 1
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For a given wiki corpus, generate features for it')
	parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
						help='files to be processed')
	parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
	parser.add_argument('--cores', default=1, type=int, help='number of concurrent threads')
	parser.add_argument('--window_size', default=6, type=int, help='window size for cooccurrence')
	parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz ',
		 type=str, help='supported alphabet')
	args = parser.parse_args()
	print args
	print len(args.inputfiles), "files found."

	workers = []

	files_per_worker = int(len(args.inputfiles) / (1. * args.cores))
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

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
import argparse
from helper import sanitize_line
from helper import filter_with_alphabet
from helper import write_checkpoint_file
from nltk import word_tokenize
from multiprocessing import Process

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

def worker_task(files, args, worker_id):
	Counter = 0 # Number of articles processed
	file_count = 0
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
					Counter += 1
					if Counter % 5000 == 0:
						sys.stdout.write("{}: Finished processing article:{}\n".format(worker_id, Counter))
					continue

				text = word_tokenize(filter_with_alphabet(sanitize_line(line), args.alphabet))
				# text = (filter_with_alphabet(sanitize_line(line), args.alphabet).split())
				for gram_length in range(1, args.ngrams + 1):
					add_to_dict(dic, text, gram_length)
				# cast to unicode string, to lower case, remove non-alphabet characters before processing
				
		#dump the gram info	
		file_name, _ = splitext(basename(inputfile))
		with open(join(args.outputpath, file_name + ".wgram"), "w") as F:
			F.write(json.dumps(dic))

		sys.stdout.write("{}: Finished processing file:{}\n".format(worker_id, inputfile))
		file_count += 1
		# clear up
		del dic

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
		generate dump of article n-gram statistics')
	parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
						help='files to be processed')
	parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
	parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz -',
		 type=str, help='supported alphabet')
	parser.add_argument('-n', '--ngrams', metavar='n', default=3, type=int, help='store grams up to n')
	parser.add_argument('--cores', default=6, type=int, help='number of concurrent threads')

	# Macros and Constants
	args = parser.parse_args()
	print(args)

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
	# End Processing files


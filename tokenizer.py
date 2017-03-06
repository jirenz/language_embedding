"""
This file tokenize each sentences in the given file, using a given gram-set.
"""
import sys
from os import listdir
from os.path import isfile, join
import argparse
import random
import json
import re
import numpy as np
from helper import load_data_from_json, sanitize_line, tokenize, get_gram_label, filter_with_alphabet, mkdir_p, write_checkpoint_file
from multiprocessing import Process
from utils import default_gram_length
from utils import default_token_weight
gram_length = default_gram_length
token_weight = default_token_weight


def worker_task(articles, args, worker_id, Dict):
	random.seed(args.seed)
	sys.stdout.write("{}: Begin processing article files...\n".format(worker_id))
	article_file_count = 0
	for article_file in articles:
		sys.stdout.write("{}: Begin processing file {}\n".format(worker_id, article_file))
		# process file, tokenize
		tokenized_sentences = {} # it's a dictionary with {index:tokenized_sentence} 
		tokenized_labels = {}
		it = 0
		with open(join(args.inputpath, article_file), "r") as F:
			for line in F:
				if line.startswith("<doc") or line.startswith("</doc>"):
					continue	
				sentences = [filter_with_alphabet(s, args.alphabet) for s in re.split(args.separator, sanitize_line(line))]
				for i in range(len(sentences)):
					tmp = tokenize(Dict, sentences[i], gram_length, token_weight)
					tokenized_sentences[it] = tmp
					tokenized_labels[it] = get_gram_label(Dict_gram_to_label, tmp)
					it += 1
		with open(join(args.outputpath + "/readable_articles", article_file + ".readable"), "w") as F:
			F.write(json.dumps(tokenized_sentences))
		with open(join(args.outputpath + "/articles", article_file), "w") as F:
			F.write(json.dumps(tokenized_labels))
		article_file_count += 1
		sys.stdout.write("{}: Finished processing {}th file {}\n".format(worker_id, article_file_count, article_file))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Tokenize the given article using given gram-set')
	parser.add_argument('inputpath', type=str, help='input directory that contains all articles')
	parser.add_argument('grampath', type=str, help='input directory that contains all gram-sets')
	parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
	parser.add_argument('-o', '--outputpath', default='./wiki_tokenized', type=str, help='output path')
	parser.add_argument('-p', '--separator', default='[,.;]', type=str, help='characters that separate sentences')
	parser.add_argument('-n', '--number', default=-1, type=int, help='number of gram files we use')
	parser.add_argument('-a', '--alphabet', default='abcdefghijklmnopqrstuvwxyz -',
		 type=str, help='supported alphabet')
	parser.add_argument('--cores', default=6, type=int, help='number of concurrent threads')

	args = parser.parse_args()
	print(args)

	# Begin Extract List of files
	articles = [f for f in listdir(args.inputpath) if isfile(join(args.inputpath, f))]
	articles.sort()
	print len(articles), "article files found."

	mkdir_p(join(args.outputpath + "/readable_articles"))
	mkdir_p(join(args.outputpath + "/articles"))

	grams = [f for f in listdir(args.grampath) if isfile(join(args.grampath, f))]
	grams.sort()
	print len(grams), "gram files found."
	# End Extract List of files

	N = args.number
	if (N <= 0) or (N >= len(grams)): N = len(grams) # N is the number of gram files we use, after sorted by filename

	print "Loading grams dictionary..."
	Dict = {} # Global dictionary for gram-files
	gram_file_count = 0
	for gram_file in grams:
		load_data_from_json(Dict, join(args.grampath, gram_file))
		gram_file_count += 1
		if (gram_file_count == N): break
	print "Loading finished.\n"

	Dict_gram_to_label = {} # provide each gram with a unique number as lable
	Dict_label_to_gram = {}
	count = 0
	for key in Dict:
		Dict_gram_to_label[key] = count
		Dict_label_to_gram[count] = key
		count += 1
	with open(join(args.outputpath, "gram_label.json"), "w") as F:
		F.write(json.dumps(Dict_gram_to_label))
	with open(join(args.outputpath, "label_gram.json"), "w") as F:
		F.write(json.dumps(Dict_label_to_gram))
	print "Finish generating mapping between grams and number-label.\n"

	workers = []
	files_per_worker = int(len(articles) / (1. * args.cores)) + 1
	sys.stdout.write("{} files per worker\n".format(files_per_worker))
	for i in range(0, len(articles), files_per_worker):
		end = i + files_per_worker
		if end > len(articles):
			end = len(articles)
		files_for_worker = articles[i:end]
		p = Process(target=worker_task, args=(files_for_worker, args, i / files_per_worker, Dict))
		p.start()
		workers.append(p)
	for idx, worker in enumerate(workers):
		worker.join()
		sys.stdout.write("{}: Exited with code {}\n".format(idx, worker.exitcode))
		if worker.exitcode != 0:
			exit(1)
	write_checkpoint_file(args.outputpath)

import sys
import json
from os import listdir
from os.path import isfile, join, basename, splitext
import random
from helper import write_checkpoint_file
from multiprocessing import Process
import argparse

def worker_task(files, args, worker_id):
	for inputfile in files:
		sys.stdout.write("{}: Processing file:{}\n".format(worker_id, inputfile))
		new_result = {}
		with open(inputfile, "r") as F:
			result = json.load(F)
			for k,v in result.iteritems():
				if v > args.threashold:
					new_result[k] = v

		file_name, _ = splitext(basename(inputfile))
		with open(join(args.outputpath, file_name + ".wgram_trimmed"), "w") as F:
			F.write(json.dumps(new_result))

if __name__ == "__main__": 
	parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
		generate dump of article n-gram statistics')
	parser.add_argument('inputfiles', metavar='path', type=str, nargs='+',
						help='files to be processed')
	# parser.add_argument('-s', '--seed', default=1234, type=int, help='random seed')
	parser.add_argument('-o', '--outputpath', default='./', type=str, help='output path')
	parser.add_argument('-t', '--threashold', default=2, type=int, help='cutoff threshold, inclusive')
	parser.add_argument('--cores', default=6, type=int, help='number of concurrent threads')
	# Macros and Constants
	args = parser.parse_args()
	print(args)

	# Begin Extract List of files
	print len(args.inputfiles), "files found."
	# End Extract List of files 

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

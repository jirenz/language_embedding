import json
import argparse
parser = argparse.ArgumentParser(description='For given wikipedia dump files, \
	generate dump of article n-gram statistics')
parser.add_argument('inputpath', type=str, help='input directory')
parser.add_argument('-c', '--count', default=100, type=str, help='number of entries to show')
args = parser.parse_args()
print(args)

with open(args.inputpath, "r") as F:
	result = json.load(F)
	sorted_data = [] # sort by weight()
	for k,v in result.iteritems():
		sorted_data.append((k,v))

	print "Sorting Dictionary of size", len(sorted_data)
	sorted_data = sorted(sorted_data, key=lambda entry : entry[1], reverse=True)
	print sorted_data[:args.count]

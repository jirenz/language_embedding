# 

class SynsetReader():
	def __init__(self, file='ref/synset_description_table.ref'):
		print "synset reader loading synset descriptions from file", file
		self.off_to_description = {}
		self.description_to_off = {}
		with open(file, 'r') as f:
			for line in f:
				index = line.index(',')
				self.off_to_description[int(line[0:index])] = line[index + 1:].strip()
		for key in self.off_to_description:
			self.description_to_off[self.off_to_description[key]] = key
		print "synset reader successfully initialized"
		return self.off_to_description, self.description_to_off

	def get_description(self, offset):
		try:
			if isinstance(offset, int):
				return self.off_to_description[offset]
			if isinstance(offset, str): # ss_...
				return self.off_to_description[int(offset[3:])]
		except KeyError:
			print "synset offset ", offset, "not found"

if __name__=="__main__":	
	from nltk.corpus import wordnet as wn
	import sys

	print "writing synsets to {}".format(sys.argv[1])

	with open(sys.argv[1], 'w') as f:
		for ss in list(wn.all_synsets()):
			f.write('{},{}\n'.format(ss.offset(), ss.definition()))


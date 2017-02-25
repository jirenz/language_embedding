import json
outputdir = "/media/pear/Storage/CS224N-tmpwork/"
with open(outputdir + "training/rate_result.txt", "r") as F:
	result = json.load(F)
	print result[:1000]

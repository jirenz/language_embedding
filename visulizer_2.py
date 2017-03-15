# -*- coding: utf-8 -*-
"""
Data-visualization
Implemented by Jack Mi
----------------------
Reads the JSON file map and out put a scattered plot
Takes the json file called 'result_map.json', 
outputs png named 'result_vis.png'
"""
import sys
import json
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import IncrementalPCA
import matplotlib.pyplot as plt

import time

vector_file = sys.argv[1]

# timing mech
time_start = time.time()
all_vectors = {}
with open(vector_file, 'r') as f:
	for line in f:
		vals = line.rstrip().split(' ')
		all_vectors[vals[0]] = [float(x) for x in vals[1:]]


desps = ["bank", "money", "finance", "cash", "income", "slope", "ss_9213565", "ss_8420278"]
#  "water", "flow", "river",
# grams = ["star", "planet", "fusion", "pop", "singer", "movie", "pos_NN", "the", "a", "an"]
# grams = ["pos_NN", "pos_IN", "pos_CD", "pos_DT", "pos_JJ", "pos_NNS", "pos_CC", "pos_RB", "pos_VBN", "pos_VBD", "pos_VBZ", "pos_VB", "pos_TO", "pos_VBP", "pos_VBG", "pos_PRP", "pos_PRP$", "pos_MD", "pos_FW", "pos_WDT", "pos_NNP", "pos_JJR", "pos_WRB", "pos_WP", "pos_JJS", "pos_RP", "pos_RBR", "pos_EX", "pos_LS", "pos_RBS", "pos_SYM", "pos_PDT", "pos_WP$", "pos_UH", "pos_NNPS"]
vectors = []
grams = []

for description in desps:
	try:
		vectors.append(all_vectors[description])
	except:
		continue
	grams.append(description)



colors = ['c' for vector in vectors]

# iPCA
model = IncrementalPCA(n_components=2)

coods = model.fit_transform(vectors)
coods_T = coods.T # cache

plt.figure(figsize=(8,8), dpi=200)
plt.autoscale(True, 'both', None) # Strict autoscale
plt.scatter(coods_T[0], coods_T[1], s=30, c=colors)
for i, txt in enumerate(grams):
	plt.annotate(txt, (coods[i][0], coods[i][1]))
plt.savefig('result_vis.png', dpi='figure')


# timing mech
time_end = time.time()

print time_end-time_start
# -*- coding: utf-8 -*-
"""
Data-visualization
Implemented by Jack Mi
----------------------
Reads the JSON file map and out put a scattered plot
Takes the json file called 'result_map.json', 
outputs png named 'result_vis.png'
"""

import json
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import IncrementalPCA
import matplotlib.pyplot as plt

import time


read_file_name = 'result_map.json' # json file name
read_file_name_txt = 'vectors.txt'
label_gram_file_name = 'label_gram_selection.json'

# timing mech
time_start = time.time()

label_gram = json.load(open(label_gram_file_name))

'''
# json version of input
re_dic = json.load(open(read_file_name))
tokens = re_dic.keys()
'''

# txt version of read map (now read 100)
first_k = 1000
count = first_k
with open(read_file_name_txt, 'r') as f:
    re_dic = {}
    for line in f:
        # Optional: only plot first k terms
        #if (count <= 0):
            #break
        count -= 1
        vals = line.rstrip().split(' ')
        if vals[0] == '<unk>':
            continue
        re_dic[label_gram[vals[0]]] = [float(x) for x in vals[1:]]

'''
# Optional: reg-string-lize tokens
for index in range(len(keys)):
    keys[index] = str(keys[index])
'''
grams = re_dic.keys()
vectors = re_dic.values()

# Optional: selection process (curr: south/north + preposition)
grams_sel = []
vectors_sel = []
colors = []
with open('prepositions.txt', 'r') as f:
    prepositions = []
    for line in f:
        prep = line.rstrip()
        prepositions.append(prep)
prepositions = ['of', 'by', 'to', 'from', 'in']

'''SNEW test
for index in range(0, len(grams)):
    gram = grams[index]
    if (('south' in gram.split() or 'north' in gram.split()\
        or 'east' in gram.split() or 'west' in gram.split())\
        and ((len(gram.split()) is 1)\
        or (len(gram.split()) is 2 and gram.split()[1] in prepositions))):
        grams_sel.append(gram)
        vectors_sel.append(vectors[index])
grams = grams_sel
vectors = vectors_sel
'''
ts = []
with open('thesaurus.txt', 'r') as f:
    for line in f:
        word = line.rstrip()
        ts.append(word)

for index in range(0, len(grams)):
    gram = grams[index]
    if gram in ts:
        grams_sel.append(gram)
        vectors_sel.append(vectors[index])
        colors.append('b')
        if len(gram.split()) is 2:
            # sep
            a = gram.split()[0]
            b = gram.split()[1]
            grams_sel.append(a)
            vectors_sel.append(re_dic[a])
            colors.append('c')
            grams_sel.append(b)
            vectors_sel.append(re_dic[b])
            colors.append('c')
            # add
            grams_sel.append(a+'+'+b)
            vectors_sel.append(np.array(re_dic[a])+np.array(re_dic[b]))
            colors.append('g')
            # mean
            grams_sel.append(a+'+'+b+'/2')
            vectors_sel.append((np.array(re_dic[a])+np.array(re_dic[b]))/2.0)
            colors.append('g')
# Plot original word         
grams_sel.append('look for')
vectors_sel.append(re_dic['look for'])
colors.append('r')
# Plot var of orig word
a = 'look'
b = 'for'
grams_sel.append(a)
vectors_sel.append(re_dic[a])
colors.append('m')
grams_sel.append(b)
vectors_sel.append(re_dic[b])
colors.append('m')
# add
grams_sel.append(a+'+'+b)
vectors_sel.append(np.array(re_dic[a])+np.array(re_dic[b]))
colors.append('m')
# mean
grams_sel.append(a+'+'+b+'/2')
vectors_sel.append((np.array(re_dic[a])+np.array(re_dic[b]))/2.0)
colors.append('m')

grams = grams_sel
vectors = vectors_sel

# iPCA
model = IncrementalPCA(n_components=2)

# TSNE
#model = TSNE(n_components=2, random_state=0)

coods = model.fit_transform(vectors)
coods_T = coods.T # cache

# Optional color
# z = np.sqrt(coods_T[0]**2, coods_T[1]**2)
plt.figure(figsize=(16,16), dpi=200)
plt.autoscale(True, 'both', None) # Strict autoscale
plt.scatter(coods_T[0], coods_T[1], s=30, c=colors)
for i, txt in enumerate(grams):
    plt.annotate(txt, (coods[i][0], coods[i][1]))    
plt.savefig('result_vis.png', dpi='figure')

# timing mech
time_end = time.time()

print 'the performance of '+ str(first_k) +' used time:'
print time_end-time_start




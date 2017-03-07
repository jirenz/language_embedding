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
import matplotlib.pyplot as plt

read_file_name = 'result_map.json'

re_dic = json.load(open(read_file_name))
tokens = re_dic.keys()
'''
# Optional: reg-string-lize tokens
for index in range(len(keys)):
    keys[index] = str(keys[index])
'''
vectors = re_dic.values()
model = TSNE(n_components=2, random_state=0)
coods = model.fit_transform(vectors)
coods_T = coods.T # cache
# Optional color
# z = np.sqrt(coods_T[0]**2, coods_T[1]**2)
plt.figure(figsize=(32,32), dpi=200)
plt.autoscale(True, 'both', True) # Strict autoscale
plt.scatter(coods_T[0], coods_T[1], s=60)
plt.savefig('result_vis.png', dpi='figure')
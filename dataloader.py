"""
This file provides helper function to load a given json file and combine it to the
current dictionary.

The resulting dictionary can be quite huge.
"""

import json

def load_data_from_json(Dict, filepath):
	# load the json file in filepath
	# combine this json with existing Dict
	with open(filepath, "r") as F:
		data = json.load(F)
		for key in data:
			try:
				Dict[key] += data[key]
			except:
				Dict[key] = data[key]
	

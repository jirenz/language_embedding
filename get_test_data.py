'''
Generate a 100 article debugging dataset
'''

import sys

f_in = open(sys.argv[1], "r")
f_out = open(sys.argv[2], "w")
counter = 0
	# All articles begin with '<doc' and end with '</doc>'
for line in f_in:
	if counter >= 100:
		break
	f_out.write(line)
	if line.startswith("</doc>"):
		counter += 1
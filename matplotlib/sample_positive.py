from random import randint
import sys

fw = open(sys.argv[2], 'w')

for i in range(150):
	rnd = randint(0, 7942)
	#print rnd
	fr = open(sys.argv[1], 'r')
	for index, line in enumerate(fr):
		if index == rnd:
			fw.write(line)
	fr.close()

fw.close()
from random import randint
import sys

fw = open('test.txt', 'w')

for i in range(600):
	rnd = randint(0, 22467)
	#print rnd
	fr = open(sys.argv[1], 'r')
	for index, line in enumerate(fr):
		if index == rnd:
			fw.write(line)
	fr.close()

fw.close()
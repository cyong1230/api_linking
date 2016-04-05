from random import randint
import sys

fw = open('test_part1.txt', 'w')

for i in range(400):
	rnd = randint(0, 28755)
	#print rnd
	fr = open(sys.argv[1], 'r')
	for index, line in enumerate(fr):
		if index == rnd:
			fw.write(line)
	fr.close()

fw.close()
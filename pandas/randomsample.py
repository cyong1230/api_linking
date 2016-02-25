from random import randint

fw = open('training_sample.txt', 'w')

unit = randint(0,18387)
cnt = 0
write_flag = 0

for i in range(100):
	print i
	fr = open('pandas_filtered.txt', 'r')
	for line in fr:
		if cnt == unit:
			write_flag = 1
		else:
			write_flag = 0
				
		if write_flag == 1:
			print line 
			fw.write(line)

		if line == '\n':
			cnt += 1

	fr.close()
	unit = randint(0,18387)
	cnt = 0
	write_flag = 0

fr.close()
fw.close()
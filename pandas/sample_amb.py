from random import randint

train_rnd = [4240,3424,9291,7432,913,6026,1671,5250,960,8406,3023,259,9638,226,6727,7872,3049,3392,
5486,2784,2903,2953,1437,1174,1583,661,7508,110,1405,8111,8632,5320,5407,9403,8079,7049,9153,6668,9704,
825,8041,6866,7126,3799,2855,7567,5464,5806,3453,2433,6369,340,9033,7382,8024,8637,7816,6445,2635,9891,7065,5983,656,9657,8440,7363,145,4801,443,2239,
5641,5019,6101,5130,7712,2846,9064,6036,7545,1736,8085,3346,4544,4460,3487,4053,30,6917,5403,2689,5294,4665,7059,3435,3142,8946,6289,6775,6577,7531,8610]

fw = open('test.txt', 'w')

unit = randint(0,9902)
cnt = 0
write_flag = 0

for i in range(100):
	#fr = open('pandas_filtered.txt', 'r')	
	fr = open('pandas_filtered_amb.txt', 'r')
	for line in fr:
		if cnt == unit:
			write_flag = 1
		else:
			write_flag = 0
				
		if write_flag == 1:
			fw.write(line)

		if line == '\n':
			cnt += 1

	fr.close()
	unit = randint(0,9902)
	while unit in train_rnd:
		unit = randint(0,9902)
	cnt = 0
	write_flag = 0

fr.close()
fw.close()
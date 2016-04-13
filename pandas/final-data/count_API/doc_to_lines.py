with open("test_all_final.conll", 'w') as new_f, open("test_all_1.conll") as f:
    for line in f:
    	if line.strip():
    		new_f.write(line.replace('\n', ' '))
    	else:
    		new_f.write('\n')
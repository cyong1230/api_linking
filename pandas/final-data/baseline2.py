import sys, re

api_neg = []
api_pos = []

with open('../apidoc/pd-np-mpl-ambAPI.txt', 'r') as neg:
    for line in neg:
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_neg.append(line)

with open('../apidoc/pd-np-mpl-remove.txt', 'r') as pos:
    for line in pos:
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_pos.append(line)


fout = open(sys.argv[2], 'w')
prev_word = ''
with open(sys.argv[1], 'r') as f:
	for line in f:
		if line != '\n':
		    line = line.strip()
                    word = line.split()[0]
                    if word.endswith("()"):
                        outline = line + '\tB-API\n'
			fout.write(outline)
		    elif re.match(r'\S.*\.\S.*', word):
		    #elif any(word in api for api in api_pos):
			outline = line + '\tB-API\n'
			fout.write(outline)
                    elif word in api_neg or word in api_pos:
                        #print word, prev_word
                        if prev_word == "`":
			    outline = line + '\tB-API\n'
			    fout.write(outline)
                        else:
			    outline = line + '\tO\n'
			    fout.write(outline)
		    else:
			outline = line + '\tO\n'
			fout.write(outline)
		else:
			fout.write(line)
                prev_word = word

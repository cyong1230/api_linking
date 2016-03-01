api_list = []
with open('apidoc/all-remove.txt', 'r') as gaz:
	for line in gaz:
		line = str(line.strip())
		line = line.lower()
		api_list.append(line)

with open('apidoc/ambiguousAPI.txt', 'r') as gaz2:
	for line in gaz2:
		line = str(line.strip())
		line = "`" + line + "`"
		api_list.append(line)
#print api_list
"""
if any(api in "I am having the x-value and corresponding counts in a file. I read that as list of tuples in the following form" for api in api_list):
	print "ya"
for api in api_list:
	if api in "I am having the x-value and corresponding counts in a file. I read that as list of tuples in the following form":
		print api
"""
f = open('pandas_filtered.txt', 'w')

with open('pandas_q_a_c.txt', 'r') as fileinput:
	for i, line in enumerate(fileinput):
		if line == '\n':
			f.write(line)
		else:
			line_low = line.lower()
			if any(api in line_low for api in api_list):
				#print line 
				f.write(line)

f.close()
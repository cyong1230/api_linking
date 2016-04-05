api_list = []
with open('apidoc/real_amb.txt', 'r') as gaz:
	for line in gaz:
		if line != '\n'
			line = str(line.strip())
			line = line.lower()
			api_list.append(line)
#print api_list
"""
if any(api in "I am having the x-value and corresponding counts in a file. I read that as list of tuples in the following form" for api in api_list):
	print "ya"
for api in api_list:
	if api in "I am having the x-value and corresponding counts in a file. I read that as list of tuples in the following form":
		print api
"""
f = open('pandas_filtered_amb.txt', 'w')

with open('pandas_q_a_c.tk', 'r') as fileinput:
	for i, line in enumerate(fileinput):
		if line == '\n':
			f.write(line)
		else:
			line_low = line.lower()
			words = line_low.split()
			#print words
			if any(api in words for api in api_list):
				#print line 
				f.write(line)

f.close()
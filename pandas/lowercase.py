f = open('pandas_q_a_c.lc', 'w')
with open('pandas_q_a_c.txt', 'r') as fileinput:
   for line in fileinput:
       line = line.lower()
       f.write(line)
f.close()
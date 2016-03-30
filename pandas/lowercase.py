import sys
f = open(sys.argv[2], 'w')
with open(sys.argv[1], 'r') as fileinput:
   for line in fileinput:
       line = line.lower()
       f.write(line)
f.close()

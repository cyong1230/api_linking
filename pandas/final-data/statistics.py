# -*- coding: utf-8 -*-
import sys
import re
import os
from os.path import basename
from cStringIO import StringIO

api_neg = []
api_pos = []

#with open('../apidoc/pd-np-mpl-ambAPI.txt', 'r') as neg:
with open('../apidoc/ambiguousAPI.txt', 'r') as neg:
    for line in neg:
        if line != '\n':
            line = line.strip()
            line = line.lower()
            api_neg.append(line)

#with open('../apidoc/pd-np-mpl-remove.txt', 'r') as pos: 
with open('../apidoc/pd-np-mpl-remove-OFFICIAL.txt', 'r') as pos: 
    for line in pos: 
        if line != '\n':
            line = line.strip()
            line = line.lower()
            api_pos.append(line)
api_all = api_pos + api_neg

cnt_poly = 0
cnt_off = 0
cnt_dot = 0

f = open('stat.txt', 'r')

for line in f:
    line = line.strip()
    line = line.lower()
    
    if line in api_neg:
        #print line
        cnt_poly += 1
    elif 1:
        if line.endswith("()"):
            t_nb = line[:-2]
        else:
            t_nb = line
        t_nb = t_nb.replace(".", "\.")
        pattern = '.*' + t_nb + ".*"
        if any(re.match(pattern, api) for api in api_pos):
            cnt_off += 1
        else:
            1
            #print line
    else:
        1
        #print line
'''
        if line.endswith("()"):
            t_nb = line[:-2].lower()
            #t_nb = t[:-2]
            if t_nb in api_pos or t_nb in api_neg:
                cnt_off += 1

        if line.endswith("()"):
            t_nb = line[:-2]
            #print line
        else:
            t_nb = line

        if t_nb in api_pos: 
            cnt_off += 1

        if re.match(r'.*\..*', t_nb):
            t_conv_dot = t_nb.replace('.', '\.')
            # begin with dot
            if re.match(r'^\..*', t_nb):
                pattern = '.*' + t_conv_dot + '$'
                if any(re.match(pattern, api) for api in api_pos):
                    #print line
                    cnt_off += 1
            else:
                pattern1 = '^' + t_conv_dot +'\..*'
                pattern2 = '.*\.' + t_conv_dot + '\..*'
                pattern3 = '.*\.' + t_conv_dot + '$'
                if any( re.match(pattern1, api) or re.match(pattern2, api) or re.match(pattern3, api) for api in api_pos):
                    #print line
                    cnt_off += 1
'''
print cnt_poly
print cnt_off
#print cnt_dot
f.close()

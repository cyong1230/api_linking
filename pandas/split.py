
# -*- coding: utf-8 -*-
import sys
import re
import os
from os.path import basename
from cStringIO import StringIO

sys.path.append(os.path.join(os.path.dirname(__file__), 'mylib'))
sys.path.append('.')
from sentencesplit import sentencebreaks_to_newlines
NEWLINE_TERM_REGEX = re.compile(r'(.*?\n)')

api_list = []
with open('apidoc/real_amb.txt', 'r') as gaz:
	for line in gaz:
		line = str(line.strip())
		line = line.lower()
		api_list.append(line)

fin = open(sys.argv[1], 'r')
fout = open(sys.argv[2], 'w')
for l in fin:
	sentences = []
	l = sentencebreaks_to_newlines(l)
	sentences.extend([s for s in NEWLINE_TERM_REGEX.split(l) if s])
	for s in sentences:
		if any(api in s for api in api_list):
			fout.write(s)
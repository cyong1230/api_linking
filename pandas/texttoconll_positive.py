
# -*- coding: utf-8 -*-
import sys
import re
import os
from os.path import basename
from cStringIO import StringIO

sys.path.append(os.path.join(os.path.dirname(__file__), 'mylib'))
sys.path.append('.')
from sentencesplit import sentencebreaks_to_newlines
from mytokenizer import mytokenizer
api_neg = []
api_pos = []
'''
with open('apidoc/pd-np-mpl-ambAPI.txt', 'r') as neg:
    for line in neg:
        if line != '\n':
            line = line.strip()
            line = line.lower()
            api_neg.append(line)
'''
with open('apidoc/pd-np-mpl-remove.txt', 'r') as pos: 
    for line in pos: 
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_pos.append(line)
#print api_pos

# prelabel matplotlib
with open('../matplotlib/real_amb.txt', 'r') as pos: 
    for line in pos: 
        if line != '\n':
            line = line.strip()
            #line = line.lower()
            api_pos.append(line)

def regex_or(*items):
  r = '|'.join(items)
  r = '(' + r + ')'
  return r

#  Oct23: overcome cases like i.e
API_pattern = re.compile(
    regex_or(r'^(?:[a-zA-Z_][a-zA-Z_]+\.)+[a-zA-Z_][a-zA-Z_]+\(\)$',
    r'^[a-zA-Z\.\_][a-zA-Z\.\_]+\(\)$',
    r'^(?:[a-zA-Z_][a-zA-Z_]+\.)+[a-zA-Z_][a-zA-Z_]+$',
    r'^(?:[A-Za-z]+)+[A-Z][a-z]+$' )
    )

# TOKENIZATION_REGEX = re.compile(API)
NEWLINE_TERM_REGEX = re.compile(r'(.*?\n)')

def text_to_conll(f):
    """Convert plain text into CoNLL format."""
    sentences = []
    for l in f:
        l = sentencebreaks_to_newlines(l)
        sentences.extend([s for s in NEWLINE_TERM_REGEX.split(l) if s])

    lines = []
    for s in sentences:
        nonspace_token_seen = False
        tokens = [t for t in s.split() if t]
        for i,t in enumerate(tokens):
            if not t.isspace():

                if t.endswith("()"):
                    #t_nb = t[:-2].lower()
                    t_nb = t[:-2]
                    if t_nb in api_pos or t_nb in api_neg:
                        lines.append([t, 'B-API'])
                        #print '111'
                        nonspace_token_seen = True
                        continue

                if t.endswith("()"):
                    #t_nb = t[:-2].lower()
                    t_nb = t[:-2]
                else:
                    #t_nb = t.lower()
                    t_nb = t

                if t_nb in api_pos:
                    lines.append([t, 'B-API'])
                    #print t
                    #print '222'
                    nonspace_token_seen = True
                    continue

                if re.match(r'.*\..*', t_nb):
                    t_conv_dot = t_nb.replace('.', '\.')
                    # begin with dot
                    if re.match(r'^\..*', t_nb):
                        pattern = '.*' + t_conv_dot + '$'
                        if any(re.match(pattern, api) for api in api_pos):
                            lines.append([t, 'B-API'])
                            #print '333'
                            nonspace_token_seen = True
                            continue
                    else:
                        pattern1 = '^' + t_conv_dot +'\..*'
                        pattern2 = '.*\.' + t_conv_dot + '\..*'
                        pattern3 = '.*\.' + t_conv_dot + '$'
                        if any( re.match(pattern1, api) or re.match(pattern2, api) or re.match(pattern3, api) for api in api_pos):
                            lines.append([t, 'B-API'])
                            #print '444'
                            nonspace_token_seen = True
                            continue

                lines.append([t, 'O'])
                nonspace_token_seen = True
        # sentences delimited by empty lines
        if nonspace_token_seen:
            lines.append([])

    lines = [[l[0], l[1]] if l else l for l in lines]
    return StringIO('\n'.join(('\t'.join(l) for l in lines)))


def main(arg1, arg2):    
    '''
    if arg1.endswith('.txt'):
        filebase = '.'.join(arg1.split('.')[:-1]) if '.' in arg1 else arg1
    tokenfile = str(filebase) + '.tk'

    mytokenizer.tokenize(arg1, tokenfile)
    f = open(tokenfile, 'r')
    '''
    f = open(arg1, 'r')
    lines = text_to_conll(f)
    with open(arg2, 'wt') as of:
        of.write(''.join(lines))

if __name__ == '__main__':
    main(*sys.argv[1:])


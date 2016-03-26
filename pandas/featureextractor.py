# -*- coding: utf-8 -*-
import sys
import re
import os
import string
import subprocess

def GetOrthographicFeatures(word):
    ngram = 5

    features = ''
    features += word.lower() + '\t'

    # prefix and suffix features
    for i in range(1, ngram+1):
        if(len(word) >= i):
            features += word[0:i].lower() + '\t'
        else:
            features += '-\t'

    for i in range(1, ngram+1):
        if(len(word) >= i):
            features += word[len(word)-i:len(word)].lower() + '\t'
        else:
            features += '-\t'

    # has dot
    if re.match(r'.*\..*', word):
        features += '1\t'
    else:
        features += '0\t'

    # has () at the end
    if re.match(r'.*\(\)$', word):
        features += '1\t'
    else:
        features += '0\t'

    # contains underscore
    if re.match(r'.*\_.*', word):
        features += '1\t'
    else:
        features += '0\t'

    return features

def GetWordClusterFeatures(word, dict):
    features = ''
    word_low = word.lower()
    if dict.has_key(word_low):
        path = str(dict.get(word_low))
    else:
        path = 'null'

    if len(path) >= 4:
        features += path[:4] + '\t'
    else:
        features += path + '\t'
    if len(path) >= 6:
        features += path[:6] + '\t'
    else:
        features += path + '\t'
    if len(path) >= 8:
        features += path[:8] + '\t'
    else:
        features += path + '\t'
    if len(path) >= 10:
        features += path[:10]+ '\t'
    else:
        features += path + '\t'
    if len(path) >= 12:
        features += path[:12] + '\t'
    else:
        features += path + '\t'
    if len(path) >= 13:
        features += path[:13] + '\t'
    else:
        features += path + '\t'
    #print features
    return features

def GetGazetteerFeatures(word):
    features = ''
    #if word.lower() in AndroidClass:
    #    features += 'isAndroidClass\t'
    #else:
    #    features += 'notAndroidClass\t'
    return features


if __name__=='__main__':

    f = open('paths', 'r')  # open word cluster file
    word_cluster_dict = {}
    for line in f:
        word_cluster_dict[line.split()[1]] = line.split()[0]
    f.close()

    fin = open(sys.argv[1], 'r')
    fout = open(sys.argv[2], 'w')

    for line in fin:
        line = line.strip()
        if line:
            (word, label) = line.split('\t')
            OrthographicFeatures = GetOrthographicFeatures(word)
            ClusterFeatures = GetWordClusterFeatures(word, word_cluster_dict)
            GazFeatures = GetGazetteerFeatures(word)
            allfeatures = word + '\t' + OrthographicFeatures + ClusterFeatures + GazFeatures + label
            fout.write(allfeatures + '\n')
        else:
            fout.write('\n')
    fout.close()
    fin.close()

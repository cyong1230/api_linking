#!/bin/zsh
crf_learn template train.data model -t
crf_test -v1 -m model test.data > crfresult1
crf_test -v1 -m model test2.data > crfresult2

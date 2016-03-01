#!/bin/zsh
crf_learn template train.data model -t
crf_test -v1 -m model test.data > crfresult

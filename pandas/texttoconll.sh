#!/bin/zsh

for f in ./sodata/*.txt
do
	filename=$(basename $f)
	filename="${filename%.*}"
	python texttoconll.py $f ${filename}.conll
	mv ${filename}.conll ./sodata
done


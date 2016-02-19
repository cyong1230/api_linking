#!/bin/zsh

for f in ./sodata/*.conll
do
	python conll02tostandoff.py -o ./input2brat $f
done

cp ./input2brat/* ~/brat/data/apilinking

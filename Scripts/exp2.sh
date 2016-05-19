#!/usr/bin/env bash

rm err/*
rm out/*
for i in `seq 1 30`;
do
	bsub -W 400 -n 1 -o ./out/out.%J -e ./err/err.%J /share/jchen37/miniconda/bin/python2.7 exp2.py $i
done

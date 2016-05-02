#!/usr/bin/env bash

rm err/*
rm out/*
for i in `seq 0 9`;
do
	bsub -W 500 -n 1 -o ./out/out.%J -e ./err/err.%J /share/jchen37/miniconda/bin/python2.7 get_hofs.py $i
done
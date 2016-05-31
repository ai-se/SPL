#!/usr/bin/env bash

rm err/*
rm out/*
for i in `seq 1 30`;
do
	bsub -W 1300 -n 1 -o ./out/out.%J -e ./err/err.%J PYTHONPATH=/gpfs_common/share/jchen37/SPL /share/jchen37/miniconda/bin/python2.7 exp3.py $i
done

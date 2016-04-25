for i in `seq 0 9`;
do
	bsub -W 300 -n 1 -o ./out/out.%J -e ./err/err.%J /share/jchen37/miniconda/bin/python2.7 IbeaDiscover.py $i
done


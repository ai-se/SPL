rm err/*
rm out/*
for alg in IbeaDiscover.py MoeadDiscover.py Nsga2Discover.py Nsga3Discover.py Spea2Discover.py; do
  for i in `seq 0 9`; do
     bsub -W 300 -n 1 -o ./out/out.%J -e ./err/err.%J /share/jchen37/miniconda/bin/python2.7 $alg $i
  done
done

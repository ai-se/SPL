import pdb, traceback, sys
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Parser.ftmodel import FTModel

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def write_random_individuals(name, num_of_individuals=100):
    ft_model = FTModel(name, num_of_attached_objs=2, setConVioAsObj=True)
    cans = [ft_model.genRandomCanBrute() for _ in range(num_of_individuals)]
    map(ft_model.eval, cans)

    feas = [can.scores[2] for can in cans]
    print max(feas)
    print min(feas)
    pdb.set_trace()

if __name__ == '__main__':
    try:
        write_random_individuals('eshop', 100)
    except:
        type, value, tb = sys.exc_info()
        # traceback.print_exc()
        # pdb.post_mortem(tb)

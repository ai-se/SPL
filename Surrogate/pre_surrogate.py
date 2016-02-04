import pdb
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Parser.parser import FTModel

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def main(name):
    m = FTModel(name, setConVioAsObj=False)
    m.printModelInfo()
    # can = m.genRandomCan(guranteeOK=True)
    # m.eval(can,doNorm=False)
    pdb.set_trace()


if __name__ == '__main__':
    main('eshop')

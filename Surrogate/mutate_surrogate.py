from __future__ import division
import logging
import traceback
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Parser.ftmodel import FTModel
from Parser.parser import *
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def test(name):
    m = FTModel(name)
    pdb.set_trace()

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG, format='Line %(lineno)d info:  %(message)s')
        test('eis')
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


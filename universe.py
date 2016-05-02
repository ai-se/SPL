from os import sys, path

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

FT_EVAL_COUNTER = 0
PROJECT_PATH, _ = [i for i in sys.path if i.endswith('SPL')][0], \
                  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

print PROJECT_PATH
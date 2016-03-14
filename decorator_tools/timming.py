import time
import logging

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def timer(disable=False):
    def _timer(func):
        def __timer(*args):
            start = time.time()
            res = func(*args)
            end = time.time()
            if not disable:
                logging.info("time consuming for **" + func.__name__ + "**: " + str(end-start))
            return res
        return __timer
    return _timer

"""
@timer()
def test_ing_log(a,b,c,d):
    for i in range(a**7):
        i
    return i


logging.basicConfig(level=logging.INFO)
print test_ing_log(4,3,2,1)
"""
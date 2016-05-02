from os import sys, path
from random import choice

from discoverer import Discoverer

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from model import candidate

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class BruteDiscoverer(Discoverer):
    def __init__(self, ft_model):
        self.ft_model = ft_model

    def gen_valid_one(self, valid_sure=True):
        def rand_list(n):
            return [choice([0, 1]) for _ in range(n)]

        while True:
            can = candidate(decs=rand_list(len(self.ft_model.dec)), fitness=[])
            if not valid_sure or self.ft_model.ok(can):
                break

        return can

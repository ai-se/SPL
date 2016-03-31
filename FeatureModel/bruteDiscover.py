from discoverer import Discoverer
from random import choice
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from GALE.model import candidate

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class BruteDiscoverer(Discoverer):
    def __init__(self, ft_model):
        super(self)
        self.ft_model = ft_model

    def gen_valid_one(self, return_fulfill=False, valid_sure=True):
        def rand_list(n):
            return [choice([0, 1]) for _ in range(n)]

        while True:
            can = candidate(decs=rand_list(len(self.ft_model.dec)), scores=[])
            if not valid_sure or self.ft_model.ok(can):
                break

        if return_fulfill:
            return can.fulfill

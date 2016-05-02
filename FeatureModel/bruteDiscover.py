from os import sys, path
from random import choice
from discoverer import Discoverer
from FeatureModel import FeatureModel
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from universe import PROJECT_PATH
import pickle

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
            can = self.ft_model.genRandomTree()
            if not valid_sure or self.ft_model.ok(can):
                break

        return can


def get_hof(name, obj_num, nums):
    fm = FeatureModel(name, num_of_attached_objs=obj_num-2)
    bd = BruteDiscoverer(fm)
    e = set()
    for i in range(nums):
        can = bd.gen_valid_one(valid_sure=False)
        fm.eval(can)
        e.add(tuple(can.fitness))
        if i % 1000 == 0:
            e = list(e)
            e = map(list, e)
            from tools.pareto import eps_sort
            with open(PROJECT_PATH+'/input/'+name+'/'+str(obj_num)+'_objs.hof', 'w') as f:
                front = eps_sort(e)
                pickle.dump(front, f)


def get_hof_all_valid(name, obj_num, nums):
    fm = FeatureModel(name, num_of_attached_objs=obj_num-2)
    bd = BruteDiscoverer(fm)
    e = set()
    for i in range(nums):
        can = bd.gen_valid_one()
        fm.eval(can)
        e.add(tuple(can.fitness))
        if i % 1000 == 0:
            e = list(e)
            e = map(list, e)
            from tools.pareto import eps_sort
            with open(PROJECT_PATH+'/input/'+name+'/'+str(obj_num)+'_objs.validhof', 'w') as f:
                front = eps_sort(e)
                pickle.dump(front, f)

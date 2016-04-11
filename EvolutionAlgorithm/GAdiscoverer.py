from __future__ import division
from __init__ import *
from FeatureModel.ftmodel import FTModel, EcsFTModel
from FeatureModel.discoverer import Discoverer
from Observers import individuals_observer
import random
import ecspy
import pdb

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "2.0"
__email__ = "jchen37@ncsu.edu"


class GADiscover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            feature_model = FTModel(name, num_of_attached_objs=len(feature_model)-2, setConVioAsObj=True)

        self.feature_model = feature_model
        self.ft = feature_model.ft

        self.ecs_model = EcsFTModel(self.feature_model)
        self.ea = ecspy.ec.GA(random.Random())

    def gen_valid_one(self):
        problem = self.ecs_model
        self.ea.observer = [individuals_observer]
        self.ea.terminator = ecspy.terminators.evaluation_termination
        ind_file_name = 'iii.csv'
        ind_file = open(ind_file_name, 'w')
        final_pop = self.ea.evolve(generator=problem.generator,
                                   evaluator=problem.evaluator,
                                   pop_size=100,
                                   maximize=problem.maximize,
                                   bounder=problem.bounder,
                                   num_selected=100,
                                   max_evaluations=1000,
                                   mutation_rate=0.3,
                                   individuals_file=ind_file)
        ind_file.close()
        valid_pop = filter(lambda p: p.fitness[1] == 0, final_pop)
        pdb.set_trace()

def demo(name):
    g = GADiscover(FTModel(name, setConVioAsObj=True))
    g.gen_valid_one()
    pdb.set_trace()

if __name__ == '__main__':
    demo('webportal')


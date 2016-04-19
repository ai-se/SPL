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


class NsgaIIDiscover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            feature_model = FTModel(name, num_of_attached_objs=len(feature_model)-2, setConVioAsObj=True)

        self.feature_model = feature_model
        self.ft = feature_model.ft

        self.ecs_model = EcsFTModel(self.feature_model)
        self.ea = ecspy.emo.NSGA2(random.Random())
        self.ea.variator = [ecspy.variators.bit_flip_mutation]
        self.ea.terminator = ecspy.terminators.generation_termination

    def gen_valid_one(self):
        problem = self.ecs_model
        self.ea.observer = [individuals_observer]

        ind_file_name = 'inds.csv'
        ind_file = open(ind_file_name, 'w')
        stat_file_name = 'stat.csv'
        stat_file = open(stat_file_name, 'w')

        final_pop = self.ea.evolve(generator=problem.generator,
                                   evaluator=problem.evaluator,
                                   pop_size=100,
                                   maximize=problem.maximize,
                                   bounder=problem.bounder,
                                   num_selected=100,
                                   max_generations=10,
                                   mutation_rate=0.3,
                                   individuals_file=ind_file,
                                   statistics_file=stat_file)
        ind_file.close()
        valid_pop = filter(lambda p: p.fitness[1] == 0, final_pop)
        return valid_pop


def demo(name):
    g = NsgaIIDiscover(FTModel(name, setConVioAsObj=True))
    ff = g.gen_valid_one()
    qq = map(EcsFTModel.ecs_individual2ft_candidate, ff)
    pdb.set_trace()

if __name__ == '__main__':
    demo('webportal')


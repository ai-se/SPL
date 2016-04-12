from __future__ import division
from __init__ import *
from FeatureModel.ftmodel import FTModel, EcsFTModel
from FeatureModel.discoverer import Discoverer
from Observers import individuals_observer
from NSGA3 import NSGA3
import random
import ecspy
import time
import pdb


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "2.0"
__email__ = "jchen37@ncsu.edu"


class Nsga3discover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            feature_model = FTModel(name, num_of_attached_objs=len(feature_model)-2, setConVioAsObj=True)

        self.feature_model = feature_model
        self.ft = feature_model.ft

        self.ecs_model = EcsFTModel(self.feature_model)
        self.ea = NSGA3(random.Random())
        self.ea.variator = [ecspy.variators.bit_flip_mutation]
        self.ea.terminator = ecspy.terminators.generation_termination

    def gen_valid_one(self):
        problem = self.ecs_model
        final_pop = self.ea.evolve(generator=problem.generator,
                                   evaluator=problem.evaluator,
                                   pop_size=50,
                                   maximize=problem.maximize,
                                   bounder=problem.bounder,
                                   max_generations=3,
                                   mutation_rate=0.3)
        valid_pop = filter(lambda p: p.fitness[1] == 0, final_pop)
        return EcsFTModel.ecs_individual2ft_candidate(valid_pop[0])

    def run(self):
        problem = self.ecs_model
        self.ea.observer = [individuals_observer]

        ind_file_name = '{0}/Records/NSGA3_{1}_{2}_inds.csv'.format(project_path, self.feature_model.name,
                                                                    time.strftime('%y%m%d'))

        ind_file = open(ind_file_name, 'w')
        stat_file_name = '{0}/Records/NSGA3_{1}_{2}_stat.csv'.format(project_path, self.feature_model.name,
                                                                     time.strftime('%y%m%d'))
        stat_file = open(stat_file_name, 'w')

        final_pop = self.ea.evolve(generator=problem.generator,
                                   evaluator=problem.evaluator,
                                   pop_size=300,
                                   maximize=problem.maximize,
                                   bounder=problem.bounder,
                                   max_generations=20,
                                   mutation_rate=0.3,
                                   individuals_file=ind_file,
                                   statistics_file=stat_file)
        ind_file.close()
        stat_file.close()


def demo(name):
    g = Nsga3discover(FTModel(name, setConVioAsObj=True))
    g.run()

if __name__ == '__main__':
    demo('eis')


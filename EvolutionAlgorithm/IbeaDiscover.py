from __future__ import division
from __init__ import *
from deap import base, creator, tools, algorithms
from deap.benchmarks.tools import hypervolume
from FeatureModel.ftmodel import FTModel
from FeatureModel.discoverer import Discoverer
from GALE.model import *
import time
import random
import pdb

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

ft = FTModel("webportal")


def eval_func(dec_l):
    candidate = o(decs=dec_l)
    ft.eval(candidate)
    return tuple(candidate.scores)


def binMutate(individual, mutate_rate):
    for i in xrange(len(individual)):
        if random.random() < mutate_rate:
            individual[i] = 1- individual[i]
    return individual,


def hv(front):
    from tools.hv import HyperVolume
    referencePoint = [1] * ft.objNum
    hv = HyperVolume(referencePoint)
    return hv.compute(front)


def valid_rate(individual_objs):
    uniques = set(map(tuple, individual_objs))
    n = len(uniques)
    valid = len([1 for i in uniques if i[1] == 0])
    return valid/n


def timestamp(p, t=0):
    return time.time()-t


class IbeaDiscover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            ft = FTModel(name, num_of_attached_objs=len(feature_model) - 2, setConVioAsObj=True)
        else:
            ft = feature_model

        creator.create("EqWeiFitnessMin", base.Fitness, weights=[-1.0] * ft.objNum)
        creator.create("Individual", list, fitness=creator.EqWeiFitnessMin)

        toolbox = base.Toolbox()

        toolbox.register("randBin", lambda: int(random.choice([0, 1])))
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.randBin, n=ft.decNum)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", eval_func)

        toolbox.register(
            "mate",
            tools.cxTwoPoint)

        toolbox.register(
            "mutate",
            binMutate,
            mutate_rate=0.15)

        toolbox.register("select", tools.selIBEA)

        self.toolbox = toolbox

    def gen_valid_one(self):
        assert False, "Do not use this function. Function not provided at this time."
        pass

    def run(self):
        toolbox = self.toolbox

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("valid_rate", valid_rate)
        stats.register("hv", hv)
        stats.register("timestamp", timestamp, t=time.time())

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "valid_rate", "hv", "timestamp"

        NGEN = 50
        MU = 1000
        CXPB = 0.9

        pop = toolbox.population(n=MU)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        record = stats.compile(pop)
        logbook.record(gen=0, evals=len(invalid_ind), **record)
        print(logbook.stream)
        algorithms.eaAlphaMuPlusLambda(pop, toolbox,
                                       MU, None, CXPB, 1.0 - CXPB, NGEN, stats)

        print("Final population hypervolume is %f" % hypervolume(pop, [1] * ft.objNum))

        return pop, logbook



ed = IbeaDiscover(FTModel(sys.argv[1]))
pop, logbook=ed.run()

import pickle
with open('pop_ibda_'+sys.argv[1], 'wb') as f:
    pickle.dump(pop, f)

pdb.set_trace()
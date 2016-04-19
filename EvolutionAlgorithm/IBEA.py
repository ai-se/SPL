from __future__ import division
from __init__ import *
from deap import base, creator, tools, algorithms
from deap.benchmarks.tools import hypervolume
from FeatureModel.ftmodel import FTModel
from GALE.model import *
import random
import pdb

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

ft = FTModel("simple")


def eval_func(dec_l):
    candidate = o(decs=dec_l)
    ft.eval(candidate)
    return tuple(candidate.scores)


def binMutate(individual, mutate_rate):
    for i in xrange(len(individual)):
        if random.random() < mutate_rate:
            individual[i] = 1- individual[i]
    return individual,

creator.create("EqWeiFitnessMin", base.Fitness, weights=[-1.0] * ft.objNum)
creator.create("Individual", list, fitness=creator.EqWeiFitnessMin)

toolbox = base.Toolbox()

num_init_pop = 1000

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


def main(seed=None):
    """Main"""
    random.seed(seed)

    NGEN = 50
    MU = 100
    CXPB = 0.9

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

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

    print("Final population hypervolume is %f" % hypervolume(pop, [1]*ft.objNum))

    return pop, logbook

a,b = main()
pdb.set_trace()
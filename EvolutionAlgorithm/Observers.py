from __future__ import division
import time
import pdb
from candidatesMeasure import analysis_cans
from FeatureModel.ftmodel import EcsFTModel

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def individuals_observer(population, num_generations, num_evaluations, args):
    # Import the necessary libraries here. Otherwise, they would have to be
    # installed even if this function is not called.
    try:
        individuals_file = args['individuals_file']
    except KeyError:
        individuals_file = open('ecspy-individuals-file-' + time.strftime('%m%d%Y-%H%M%S') + '.csv', 'w')
    try:
        statistics_file = args['statistics_file']
    except KeyError:
        statistics_file = open('ecspy-statistics-file-' + time.strftime('%m%d%Y-%H%M%S') + '.csv', 'w')

    population = list(population)
    for i, p in enumerate(population):
        individuals_file.write('{0}, {1}, {2}, {3}\n'.format(num_generations, i, p.fitness, str(p.candidate)))
    individuals_file.flush()

    valid_pop = [p for p in population if p.fitness[1] == 0]
    valid_pop = map(EcsFTModel.ecs_individual2ft_candidate, valid_pop)
    hv = analysis_cans(valid_pop, all_non_dominated=False)

    valid_rate = len(valid_pop) / len(population)

    if num_generations == 0:
        statistics_file.write('generation, evaluations, valid_rate, hypervolume, timestamp\n')

    statistics_file.write('{0}, {1}, {2}, {3}, {4}\n'.
                          format(num_generations, num_evaluations, valid_rate, hv, time.time()))
    statistics_file.flush()

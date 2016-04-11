import time

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

    population = list(population)
    for i, p in enumerate(population):
        individuals_file.write('{0}, {1}, {2}, {3}\n'.format(num_generations, i, p.fitness, str(p.candidate)))
    individuals_file.flush()

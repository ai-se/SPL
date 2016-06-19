#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016, Jianfeng Chen <jchen37@ncsu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.


from __future__ import division
from os import path
from deap import creator, base
from deap.tools.emo import sortNondominated
import glob
import sys
import pdb

sys.dont_write_btyecode = True


"""
get the optimal in objectives among all repetitions and runnings.
"""

PROJECT_PATH, _ = [i for i in sys.path if i.endswith('SPL')][0], \
                  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

folders = [PROJECT_PATH+'/j_res',
           '/Users/jianfeng/Desktop/hpc_jres',
           '/Users/jianfeng/Desktop/j_res_sat']


def _get_frontier(pop):
    """
    return the pareto frontier of the given pop. No duplicate individuals in the returns
    :param pop:
    :return:
    """
    front = sortNondominated(pop, len(pop), True)[0]
    uniques = []
    for f in front:
        if f.fitness.values not in uniques:
            uniques.append(f.fitness.values)
    return uniques


def print_out_optimals(model_name):
    files = []
    for fd in folders:
        files.extend(glob.glob(fd + '/*.txt'))
    files = filter(lambda f: model_name in f, files)

    valid_objs = set()
    for records in files:
        with open(records, 'r') as f:
            lines = f.readlines()
            lines = map(lambda x: x.rstrip(), lines)
            start = lines.index("~~~")
            fits = lines[start + 1:-2]
            for fit in fits:
                if fit.startswith('0.0'):
                    valid_objs.add(fit)

    valid_objs = map(lambda x: map(float, x.split(' ')), valid_objs)

    creator.create("FitnessMin", base.Fitness, weights=[-1.0] * 5)
    creator.create("Individual", list, fitness=creator.FitnessMin)

    pop = list()
    for i in valid_objs:
        ind = creator.Individual([])
        ind.fitness = creator.FitnessMin(i)
        pop.append(ind)
    frontier = _get_frontier(pop)

    with open(PROJECT_PATH+'/optimal_in_his/'+model_name+'.txt', 'w') as f:
        f.write('~~~\n')
        for fer in frontier:
            f.write(' '.join(map(str, fer)))
            f.write('\n')
try:
    model = sys.argv[1]
except:
    model = 'linux'
print_out_optimals(model)

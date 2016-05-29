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
from deap.tools.emo import sortNondominated
from deap.benchmarks.tools import diversity, convergence
import sys
import pickle
import time
from tools.hv import HyperVolume
from universe import PROJECT_PATH as project_path

sys.dont_write_btyecode = True


def _get_frontier(pop):
    """
    return the pareto frontier of the given pop. No duplicate individuals in the returns
    :param pop:
    :return:
    """
    front = sortNondominated(pop, len(pop), True)[0]
    uniques = []
    for f in front:
        if f not in uniques:
            uniques.append(f)
    return uniques


def stat_basing_on_pop(pop, record_valid_only, optimal_in_theory=None):
    """
    return some statstics basing on the populations
    :param pop:
    :param optimal_in_theory:
    :param record_valid_only:
    :return:
        * hyper_volume
        * spread
        * IGD
        * frontier_size
        * valid_frontier_size
    """
    if record_valid_only:
        pop = filter(lambda p: p.fitness.correct, pop)

    if len(pop) == 0:
        return 0, 0, 0, 0, 0

    front = _get_frontier(pop)

    front_objs = [f.fitness.values for f in front]

    reference_point = [1] * len(front_objs[0])
    hv = HyperVolume(reference_point).compute(front_objs)  # did NOT use deap module calc

    sort_front_by_obj0 = sorted(front, key=lambda f: f.fitness.values[0], reverse=True)
    first, last = sort_front_by_obj0[0], sort_front_by_obj0[-1]
    spread = diversity(front, first, last)

    if optimal_in_theory == 'None':  # not available!!
        IGD = -1
    else:
        IGD = convergence(front, optimal_in_theory)

    frontier_size = len(front)
    valid_frontier_size = len([i for i in pop if i.fitness.correct])

    return round(hv, 3), round(spread, 3), round(IGD, 3), frontier_size, valid_frontier_size


def timestamp(p, t=0):
    return time.time() - t


def pickle_results(model_name, alg_name, pop, logbook):
    pop_file_name = '{0}/Records/{1}_{2}_{3}.pop'.format(project_path, alg_name, model_name, time.strftime('%m%d%y'))
    log_file_name = '{0}/Records/{1}_{2}_{3}.logbook'.format(project_path, alg_name, model_name, time.strftime('%m%d%y'))

    with open(pop_file_name, 'wb') as f:
        pickle.dump(pop, f)

    with open(log_file_name, 'wb') as f:
        pickle.dump(logbook, f)


def true_candidate_collector(model_name, pop):
    archives_file_name = '{0}/input/{1}.true_can.txt'.format(project_path, model_name)
    valid_pop = filter(lambda p: p.fitness.correct, pop)

    with open(archives_file_name, 'a') as f:
        existed = []
        for i in f.readline():
            existed.append(i)

        toadd = []
        for p in valid_pop:
            if p not in existed:
                toadd.append(p)

        import pdb
        pdb.set_trace()
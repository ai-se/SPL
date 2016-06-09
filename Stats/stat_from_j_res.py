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
from deap.benchmarks.tools import diversity, convergence
from deap import creator, base
from deap.tools.emo import sortNondominated
from Stats.hv import HyperVolume
from Stats.o import *
import sys
import pdb

sys.dont_write_btyecode = True


def dominates(row, rowCandidate):
    return all(r >= rc for r, rc in zip(row, rowCandidate))


def cull(pts):
    dominated = []
    cleared = []
    remaining = pts
    while remaining:
        candidate = remaining[0]
        new_remaining = []
        for other in remaining[1:]:
            [new_remaining, dominated][dominates(candidate, other)].append(other)
        if not any(dominates(other, candidate) for other in new_remaining):
            cleared.append(candidate)
        else:
            dominated.append(candidate)
        remaining = new_remaining
    return cleared, dominated


def _get_frontier(pop):
    """
    return the pareto frontier of the given pop. No duplicate individuals in the returns
    :param pop:
    :return:
    """
    _, front = cull(pop)
    uniques = []
    for f in front:
        if f not in uniques:
            uniques.append(f)
    return uniques


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
        * valid_rate
    """
    vpop = filter(lambda p: p.fitness.correct, pop)
    if len(pop) == 0:
        return 0, 0, 0, 0, 0

    if record_valid_only and len(vpop) == 0:
        return 0, 0, 0, 0, 0

    front = _get_frontier(vpop) if record_valid_only else _get_frontier(pop)

    front_objs = [f.fitness.values for f in front]
    reference_point = [1] * len(front_objs[0])
    hv = HyperVolume(reference_point).compute(front_objs)  # did NOT use deap module calc
    sort_front_by_obj0 = sorted(front, key=lambda f: f.fitness.values[1], reverse=True)

    first, last = sort_front_by_obj0[0], sort_front_by_obj0[-1]
    spread = diversity(front, first, last)

    if optimal_in_theory is None:  # not available!!
        IGD = -1
    else:
        IGD = convergence(front, optimal_in_theory)

    frontier_size = len(front)
    valid_rate = len(vpop) / len(pop)

    return round(hv, 3), round(spread, 3), round(IGD, 3), frontier_size, valid_rate


def get_stats(model_name, j_res_file_name):
    PROJECT_PATH, _ = [i for i in sys.path if i.endswith('SPL')][0], \
                      sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    def get_obj_max():
        with open(PROJECT_PATH+'/dimacs_data/'+model_name+'.dimacs.augment', 'r') as f:
            lines = f.readlines()
            lines = filter(lambda l: not l.startswith('#'), lines)  # filter the comment line. usually the first line
            lines = map(lambda x: x.rstrip(), lines)  # delete the \n letter
            lines = map(lambda x:x.split(" "), lines)
            linesT = map(list, zip(*lines))
            featureIndex = map(int, linesT[0])
            cost = map(float, linesT[1])
            # used_before = map(int, linesT[2])
            defects = map(int, linesT[3])

        with open(PROJECT_PATH+'/dimacs_data/'+model_name+'.dimacs', 'r') as f:
            lines = f.readlines()
            indicator = filter(lambda l: l.startswith("p cnf "), lines)[0]
            indicator.rstrip()
            cnfNum = int(indicator.split(" ")[-1])

        objMax = [cnfNum, max(featureIndex), max(featureIndex), sum(defects), sum(cost)]
        return objMax

    def normalize(fitness, objMax):
        for o_i, o in enumerate(fitness):
            fitness[o_i] = o / objMax[o_i]

    with open(PROJECT_PATH+'/j_res/'+j_res_file_name, 'r') as f:
        lines = f.readlines()
        lines = map(lambda x: x.rstrip(), lines)
        start = lines.index("~~~")
        decs = lines[:start]
        print(len(set(decs)))
        fits = lines[start+1:-2]
        runtime = float(lines[-1])
        print("runtime: %f" % runtime)
        pop_fitness = map(lambda x: x.split(" "), fits)
        for p_i, p in enumerate(pop_fitness):
            pop_fitness[p_i] = map(float, p)

    obj_max = get_obj_max()

    creator.create("FitnessMin", base.Fitness, weights=[-1.0] * 5, correct=bool, conVio=list)
    creator.create("Individual", list, fitness=creator.FitnessMin, fulfill=list)

    pop = list()
    for d, p in zip(decs, pop_fitness):
        ind = creator.Individual(map(int, list(d)))
        correct = p[0] < 0.01
        normalize(p, obj_max)
        ind.fitness = creator.FitnessMin(p)
        ind.fitness.correct = correct
        pop.append(ind)

    return stat_basing_on_pop(pop, record_valid_only=False)

import debug
print get_stats("eshop", "eshop_SATIBEA_50k_1.txt")

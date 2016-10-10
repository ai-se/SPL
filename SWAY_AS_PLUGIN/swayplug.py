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
from deap import tools
from ProductLine.DimacsModel import DimacsModel
from Stats.stat_from_j_res import stat_basing_on_pop
from deap.algorithms import varAnd
import pdb
import copy
import csv
import os
import random
import deap

"""
Let the result of sway as the initial generation of the classic MOEAs.
Fly research in the conference SSBSE16
"""

name = 'webportal'


def load_sway_results(model):
    fs = [f for f in os.listdir('../j_res/SWAY4_D') if model.name in f]
    filename = random.choice(fs)
    with open('../j_res/SWAY4_D/'+filename, 'r') as f:
        content = f.readlines()
        candidates = content[:content.index('~~~\n')]

    candidates = map(lambda i:i[:-1], candidates)
    pops = list()
    for i in candidates:
        pops.append(model.Individual(i))
    return pops


def NSGA2(name):
    model = DimacsModel(name)
    toolbox = model.toolbox
    toolbox.register('mutate', model.bit_flip_mutate)
    toolbox.register('select', tools.selNSGA2)
    toolbox.register('mate', model.cxTwoPoint)
    # get the initial generation from the result of sway
    # and evaluate them
    pop = load_sway_results(model)
    toolbox.map(model.eval_ind, pop)

    # the parameters for NSGA-II as follows
    MU = 100
    NGEN = 100
    CXPB = 0.9

    # start the NSGA2 algorithms
    for _ in range(100-len(pop)):
        pop.append(random.choice(pop))
    random.shuffle(pop)

    for gen in range(1, NGEN):
        # vary the population
        tools.emo.assignCrowdingDist(pop)
        offspring = tools.selTournamentDCD(pop, len(pop))
        offspring = [toolbox.clone(ind) for ind in offspring]

        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= CXPB:
                toolbox.mate(ind1, ind2)
            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values

        map(model.eval, offspring)
        # Select the next generation population
        pop = toolbox.select(pop + offspring, MU)

    valid_pop = [i for i in pop if i.fitness.values[0] <=0]
    hv, spread, _, size, _ = stat_basing_on_pop(valid_pop, False)

    print(hv, spread, size)
    return hv, spread, size


def IBEA(name):
    model = DimacsModel(name)
    toolbox = model.toolbox
    toolbox.register('mutate', model.bit_flip_mutate)
    toolbox.register('select', tools.selIBEA)
    toolbox.register('mate', model.cxTwoPoint)
    toolbox.register('clone', copy.deepcopy)
    # get the initial generation from the result of sway
    # and evaluate them
    pop = load_sway_results(model)
    toolbox.map(model.eval_ind, pop)

    # the parameters for  IBEA as follows
    MU = 100
    NGEN = 100
    CXPB = 0.9

    # start the NSGA2 algorithms
    for _ in range(100-len(pop)):
        pop.append(random.choice(pop))
    random.shuffle(pop)

    parents = pop[:]
    for gen in range(1, NGEN):
        # Vary the parents
        offspring = varAnd(parents, toolbox, CXPB, 0.2)
        pop[:] = parents + offspring

        for p in pop:
            if not p.fitness.valid:
                model.eval(p)

        # Select the next generation parents
        parents[:] = toolbox.select(pop, MU)

    # pdb.set_trace()
    valid_pop = [i for i in pop if i.fitness.values[0] <=0]
    hv, spread, _, size, _ = stat_basing_on_pop(valid_pop, False)

    print(hv, spread, size)
    return hv, spread, size


if __name__ == '__main__':
    import debug
    # n = ['webportal', 'eshop', 'toybox', 'uClinux']
    # csvfile = open('../research_oct_9_nsga2.csv', 'a')
    # output = csv.writer(csvfile, delimiter=',')
    # for x in n:
    #     print(x)
    #     for i in range(10):
    #         hv, spread, size = NSGA2(x)
    #         output.writerow([x, hv, spread, size])

    n = ['webportal', 'eshop', 'toybox', 'uClinux']
    csvfile = open('../research_oct_9_ibea.csv', 'a')
    output = csv.writer(csvfile, delimiter=',')
    for x in n:
        print(x)
        for i in range(10):
            hv, spread, size = IBEA(x)
            output.writerow([x, hv, spread, size])

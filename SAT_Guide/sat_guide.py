# !/usr/bin/env python
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
from ProductLine.DimacsModel import DimacsModel
from operator import itemgetter
from copy import deepcopy
from deap import tools
from itertools import groupby, islice
# from Stats.stat_from_j_res import stat_basing_on_pop
from sway import sway
import time
import pycosat
import random
import pdb


def pycosatSol2binstr(sol):
    """
    Demo: [1, 2, 3, -4, -5, 6, -7, -8, -9, -10] -> '1110010000'
    """
    res = ['1'] * len(sol)
    for i in sol:
        if i < 0:
            res[-i-1] = '0'
    return ''.join(res)


def grouping_dimacs_model_by_sat_solver(dimacs_model):
    # results start from 0
    appendix = list()
    model = dimacs_model
    inds = []
    i = 0
    cnfs = deepcopy(model.cnfs)
    groups = list()
    while True:
        sat_engine = pycosat.itersolve(cnfs)
        i = 0
        for sol in sat_engine:
            i += 1
            if i > 100: break
            inds.append(model.Individual(pycosatSol2binstr(sol)))
        tmp = map(list, zip(*inds))
        tmp = map(lambda x: len(set(x)), tmp)
        group1 = [i for i, j in enumerate(tmp) if j > 1]

        if len(group1) > 0:
            groups.append(group1)
        else:
            break

        addition = []
        for i, j in zip(group1, itemgetter(*group1)(inds[0])):
            if j == '0':
                addition.append([-i-1])
            else:
                addition.append([i+1])

        cnfs = cnfs + addition
        appendix.extend(inds)
        inds = []

    return groups, appendix


def dist(tuple1, tuple2):
    d = 0
    for i, j in zip(tuple1, tuple2):
        if i != j:
            d += 1
    return d


def intra_group_mutate(ind, groups, appendix, model):
    s = list(ind)
    for g in groups:
        if random.random() > 0.01:
            continue
        control_group = itemgetter(*g)(s)
        t = [itemgetter(*g)(i) for i in appendix]
        dists = [dist(i, control_group) for i in t]
        target = dists.index(max(dists))

        for i in g:
            s[i] = appendix[target][i]
    return model.Individual(''.join(s))


def mate(ind1, ind2, groups, model):
    # g = deepcopy(groups)
    # random.shuffle(g)
    # g = g[:int(len(g)*0.1)]
    # g = [item for i in g for item in i]
    # s1 = list(ind1)
    # s2 = list(ind2)
    # for i in range(len(s1)):
    #     if i in g:
    #         s1[i], s2[i] = s2[i], s1[i]
    # split_point = random.randint(0, len(s1))
    # ind1 = model.Individual(''.join(s1[:split_point]+s2[split_point:]))
    # ind2 = model.Individual(''.join(s2[:split_point]+s1[split_point:]))
    # pdb.set_trace()
    # return ind1, ind2

    diff = [i for i, (x, y) in enumerate(zip(ind1, ind2)) if x != y]
    # lock the irrelevant parts
    cnfs = []
    for i in range(len(ind1)):
        if random.random() < 0.1: continue
        if i not in diff:
            if ind1[i] == '1':
                cnfs += [[i+1]]
            else:
                cnfs += [[-i-1]]
    sat_engine = pycosat.itersolve(model.cnfs + cnfs)
    l = list(islice(sat_engine, 2))
    if len(l) == 0:
        return ind1, ind2
    if len(l) == 1:
        return model.Individual(pycosatSol2binstr(l[0])), ind2
    else:
        ind1 = model.Individual(pycosatSol2binstr(l[0]))
        ind2 = model.Individual(pycosatSol2binstr(l[1]))
        # pdb.set_trace()
        return ind1, ind2


def binary_tournament_selc(population, return_size):
    parents = []
    for _ in xrange(return_size):
        # Pick individuals for tournament
        tournament = [random.choice(population) for _ in range(2)]
        # Sort according to fitness
        tournament.sort()
        # Winner is element with smallest fitness
        parents.append(tournament[0])

    return parents


def run(model, seedonly=False):
    # groups, appendix = grouping_dimacs_model_by_sat_solver(model)
    groups = []
    toolbox = model.toolbox
    NGEN = 50
    MU = 300
    CXPB = 0.04

    pop = []
    # sat_engine = pycosat.itersolve(model.cnfs)
    # for sol, _ in zip(sat_engine, range(MU)):
    #     pop.append(model.Individual(pycosatSol2binstr(sol)))

    # for i in appendix:
    #     pop.append(model.Individual(i))
    with open("/Users/jianfeng/git/SPL/tmp_seed/"+model.name+".txt", 'r') as f:
        lines = f.readlines()
        for l in lines:
            pop.append(model.Individual(l[:-1]))

    # def dominate(ind1, ind2):
    #     if not ind1.fitness.valid:
    #         model.eval(ind1)
    #     if not ind2.fitness.valid:
    #         model.eval(ind2)
    #     return ind1 < ind2

    # out = sway(pop, better=dominate, enough=MU)
    # pop = out[0]
    # for _ in range(int(MU)):
    #     # pop.append(model.get_random_bit_ind(background=appendix[0], mask=[j for i in groups for j in i]))
    #     pop.append(model.gen_random_bit_ind_r(random.uniform(0,1)))
        # appendix.append(model.get_random_bit_ind())

    random.shuffle(pop)
    pop = pop[:MU]
    for p in pop:
        if not p.fitness.valid:
            model.eval(p)

    if seedonly: return pop

    for gen in range(1, NGEN):
        for p in pop:
            if not p.fitness.valid:
                model.eval(p)
        tools.emo.assignCrowdingDist(pop)
        offspring = tools.selTournamentDCD(pop, len(pop))
        pdb.set_trace()
        offspring = [toolbox.clone(ind) for ind in offspring]

        # get the group id
        for p in offspring:
            p.gid = int(p.count('1') / len(p) * 10)
        gids = [i.gid for i in offspring]

        for k in set(gids):
            g = [ind for i, ind in enumerate(offspring) if gids[i] == k]
            if len(g) < 2: continue
            for ind1, ind2 in zip(g[::2], g[1::2]):
                if random.random() <= CXPB:
                    a = offspring.index(ind1)
                    b = offspring.index(ind2)
                    offspring[a], offspring[b] = mate(ind1, ind2, groups, model)
                    # offspring[a] = intra_group_mutate(offspring[a], groups, appendix, model)
                    # offspring[b] = intra_group_mutate(offspring[b], groups, appendix, model)
                    model.eval(offspring[a])
                    model.eval(offspring[b])
                    # pdb.set_trace()
                    # del ind1.fitness.values, ind2.fitness.values

        # for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
        #     if random.random() <= CXPB:
        #         a = offspring.index(ind1)
        #         b = offspring.index(ind2)
        #         offspring[a], offspring[b] = mate(ind1, ind2, groups, model)
        #         # offspring[a] = intra_group_mutate(offspring[a], groups, appendix, model)
        #         # offspring[b] = intra_group_mutate(offspring[b], groups, appendix, model)
        #         model.eval(offspring[a])
        #         model.eval(offspring[b])
                # pdb.set_trace()
            # del ind1.fitness.values, ind2.fitness.values

        # Select the next generation parents
        pop[:] = tools.selNSGA2(pop + offspring, MU)

    return pop


def running(model_name):
    model = DimacsModel(model_name)
    for i in range(1,3):
        t1 = time.time()
        rr = run(model)
        runtime = time.time() - t1
        with open("/Users/jianfeng/git/SPL/j_res/e.txt".format(model_name, i), "w") as f:
        # with open("/Users/jianfeng/git/SPL/j_res/{0}_SAT1_50k_{1}.txt".format(model_name, i), "w") as f:
        # with open("/Users/jianfeng/git/SPL/j_res/{0}_SWAY_{1}.txt".format(model_name, i), "w") as f:
            for r in rr:
                f.write(r)
                f.write('\n')
            f.write('~~~\n')
            for r in rr:
                f.write(' '.join(map(str, r.fitness.values)))
                f.write('\n')
            f.write('~~~\n')
            f.write(str(runtime))
            f.write('\n')

import debug
running('ecos')

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

# from ProductLine.DimacsModel import DimacsModel
# from operator import itemgetter
# from copy import deepcopy
# import pycosat
# import pdb
#
#
# def pycosatSol2binstr(sol):
#     """
#     Demo: [1, 2, 3, -4, -5, 6, -7, -8, -9, -10] -> '1110010000'
#     """
#     res = ['.'] * len(sol)
#     for i in sol:
#         if i < 0:
#             res[-i-1] = '*'
#     return ''.join(res)
#
#
# model = DimacsModel('ecos')
# inds = []
# i = 0
# cnfs = deepcopy(model.cnfs)
#
# while True:
#     sat_engine = pycosat.itersolve(cnfs)
#     i = 0
#     for sol in sat_engine:
#         i += 1
#         # if i > 1000: break
#         print pycosatSol2binstr(sol)
#         continue
#         inds.append(model.Individual(pycosatSol2binstr(sol)))
#     tmp = map(list, zip(*inds))
#     tmp = map(lambda x:len(set(x)), tmp)
#     group1 = [i for i,j in enumerate(tmp) if j > 1]
#
#     print(group1)
#
#     addition = []
#     for i, j in zip(group1, itemgetter(*group1)(inds[0])):
#         if j == '0':
#             addition.append([-i-1])
#         else:
#             addition.append([i+1])
#
#     cnfs = cnfs + addition
#     inds = []
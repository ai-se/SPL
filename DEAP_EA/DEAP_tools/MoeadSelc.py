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
import os.path
import sys

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import copy
import numpy as np
from deap import tools
import random

EPS = 0.000001

DIVISIONS = {
    # Objectives : [outer_divs, inner_divs]
    3: [12, 0],
    4: [8, 0],  # TODO need double-check
    5: [6, 0],
    8: [3, 2],
    10: [3, 2],
    15: [2, 1]
}


def splits(dim, div, outer=True):
    if outer:
        start = 0.0
        end = 1.0
    else:
        start = 1 / (2 * dim)
        end = start + 0.5
    delta = (end - start) / div
    return [start] + [start + i * delta for i in range(1, div)] + [end]


def expand(coords, possible):
    expanded = []
    for coord in coords:
        for val in possible:
            new = coord + [val]
            if valid(new):
                expanded.append(new)
            else:
                break
    return expanded


def valid(coord, exact=False):
    if exact:
        return abs(sum(coord) - 1) < EPS
    else:
        return sum(coord) <= 1 + EPS


def shuffle(lst):
    random.shuffle(lst)
    return lst


def reference(m, p, outer=True):
    """
    Create a set of reference points
    with m axes and p is the number of
    divisions along each axis
    :param m: Number of axis
    :param p: Number of divisions
    :return:
    """
    possible = splits(m, p, outer=outer)
    coords = [[pt] for pt in possible]
    for i in range(1, m):
        coords = expand(coords, possible)
    return [coord for coord in coords if valid(coord, exact=True)]


def cover(m, p_outer, p_inner=None):
    ref = reference(m, p_outer)
    if p_inner:
        ref += reference(m, p_inner, outer=False)
    return ref


def euclidean(one, two):
    dist = 0
    for o_i, t_i in zip(one, two):
        dist += (o_i - t_i) ** 2
    return dist ** 0.5


def init_weights(obj_num, population):
    """
    Initialize weights. We first check if we can generate
    uniform weights using the Das Dennis Technique.
    If not, we randomly generate them.
    :param obj_num:
    :param population:
    """
    m = obj_num

    def random_weights():
        wts = []
        for _ in population:
            wt = [random.random() for _ in xrange(m)]
            tot = sum(wt)
            wts.append([wt_i / tot for wt_i in wt])
        return wts

    divs = DIVISIONS.get(m, None)
    weights = None
    if divs:
        weights = cover(m, divs[0], divs[1])
    if weights is None or len(weights) != len(population):
        weights = random_weights()
    assert len(weights) == len(population), "Number of weights != Number of points"

    weights = shuffle(weights)
    for i in xrange(len(weights)):
        population[i].weight = weights[i]


def setup(obj_num, population, setting_T):
    """
    Mark each point with the nearest "T"
    weight vectors and return the global best.
    """
    init_weights(obj_num, population)

    for one in range(len(population)):
        distances = []
        ids = []
        for two in range(len(population)):
            if one == two:
                continue
            ids.append(two)
            distances.append(euclidean(population[one].weight, population[two].weight))
        sorted_ids = [index for dist, index in sorted(zip(distances, ids))]
        population[one].neighbor_ids = sorted_ids[:setting_T]


def cxSimulatedBinary(point, population, CXPB=0.5):
    """
    Perform Simulated Binary Crossover
    for producing mutants
    :param point: point to generate a crossover
    :param population: Population to search from
    :param CXPB:
    :return: List containing Decisions of mutant
    """
    one = random.choice(point.neighbor_ids)
    two = random.choice(point.neighbor_ids)
    while one == two:
        two = random.choice(point.neighbor_ids)
    mom = population[one]
    dad = population[two]

    if random.random() > CXPB:
        return mom

    child = tools.cxTwoPoint(mom, dad)
    return child[0]


def weighted_tch(objectives, weights):
    """
    Chebyshev distance
    """
    dist = float('-inf')
    for i in xrange(len(weights)):
        normalized = abs(objectives[i])
        if weights[i] == 0:
            normalized *= 0.0001
        else:
            normalized *= weights[i]
        dist = max(dist, normalized)
    assert dist >= 0, "Distance can't be less than 0"
    return dist


def update_neighbors(point, mutant, population):
    if hasattr(point, 'neighbor_ids') and point.neighbor_ids is not None:
        ids = point.neighbor_ids
    else:
        ids = range(len(population))

    for neighbor_id in ids:
        neighbor = population[neighbor_id]
        neighbor_distance = weighted_tch(neighbor.fitness.values, neighbor.weight)
        mutant_distance = weighted_tch(mutant.fitness.values, neighbor.weight)

        if mutant_distance < neighbor_distance:
            population[neighbor_id] = mutant
            population[neighbor_id].fitness.values = mutant.fitness.values



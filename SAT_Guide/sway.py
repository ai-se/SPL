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
import sys
from math import sqrt, exp
import random
import itertools
import pdb
sys.dont_write_btyecode = True


mins = list()
maxs = list()
evalFunc = None
evalCount = 0


def _norm(f1):
    res = list()
    for f, m, M in zip(f1, mins, maxs):
        if m == M:
            res.append(0)
        else:
            res.append((f-m)/(M-m))
    return res


def _loss(f1, f2):
    return sum(exp(i - j) for i, j in zip(f1, f2)) / len(f1)


def cont_dominate(ind1, ind2):
    """

    Args:
        ind1:
        ind2:
    ALL VALUES ARE LESS IS MORE!!!!
    Returns: whether ind1 dominates ind2, i.e. True if ind1 is better than ind2
    """
    global evalCount
    if not ind1.fitness.valid:
        evalFunc(ind1)
        evalCount += 1

    if not ind2.fitness.valid:
        evalFunc(ind2)
        evalCount += 1

    f1 = tuple(ind1.fitness.values)
    f2 = tuple(ind2.fitness.values)
    f1 = _norm(f1)
    f2 = _norm(f2)
    return _loss(f1, f2) < _loss(f2, f1)


def bin_dominate(ind1, ind2):
    """

    Args:
        ind1:
        ind2:
    ALL VALUES ARE LESS IS MORE!!!!
    Returns: whether ind1 dominates ind2, i.e. True if ind1 is better than ind2

    """
    global evalCount
    if not ind1.fitness.valid:
        evalFunc(ind1)
        evalCount += 1
    if not ind2.fitness.valid:
        evalCount += 1
        evalFunc(ind2)
    f1 = tuple(ind1.fitness.values)
    f2 = tuple(ind2.fitness.values)

    for i, j in zip(f1, f2):
        if i > j:
            return False

    if f1 == f2:
        return False
    return True


def distance(ind1, ind2):
    # Jaccard distance
    d = 0
    for i, j in zip(ind1, ind2):
        if i != j:
            d += 1
    return d


def sway(pop, ms, Ms, evalfunc, better=bin_dominate, enough=None):
    global evalCount, mins, maxs, evalFunc
    mins = ms
    maxs = Ms
    evalFunc = evalfunc
    evalCount = 0

    if enough is None:
        enough = max(sqrt(len(pop)), 20)

    def furthest(ind, items):
        res = ind
        d = 0
        for x in items:
            tmp = distance(ind, x)
            if tmp > d:
                d = tmp
                res = x
        return res

    def split(items, middle):
        rand = random.choice(items)
        east = furthest(rand, items)
        west = furthest(rand, items)
        c = distance(west, east)
        for x in items:
            a = distance(x, west)
            b = distance(x, east)
            x.d = (a*a + c*c - b*b) / (2*c + 0.0001)
            # x.d = min(a, b)
        items = sorted(items, key=lambda i: i.d)
        return west, east, items[:middle], items[middle:]

    def cluster(items, out):
        if len(items) < enough:
            out += [items]
        else:
            west, east, west_items, east_items = split(items, int(len(items)/2))
            if not better(west, east):
                cluster(west_items, out)
            else:
                cluster(east_items, out)
        return out

    res = cluster(pop, [])
    return list(itertools.chain.from_iterable(res))

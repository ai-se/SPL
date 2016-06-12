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
from math import sqrt
import random
import pdb
sys.dont_write_btyecode = True


def sway(pop, better, enough=None):
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

    def distance(ind1, ind2):
        # Jaccard distance
        d = 0
        for i, j in zip(ind1, ind2):
            if i != j:
                d += 1
        return d

    def split(items, middle):
        rand = random.choice(items)
        east = furthest(rand, items)
        west = furthest(rand, items)
        c = distance(west, east)
        for x in items:
            a = distance(x, west)
            b = distance(x, east)
            # x.d = (a*a + c*c - b*b) / (2*c + 0.0001)
            x.d = min(a, b)
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

    return cluster(pop, [])

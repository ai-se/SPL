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

import pickle
from discoverer import Discoverer
from FeatureModel import FeatureModel
from universe import PROJECT_PATH


class BruteDiscoverer(Discoverer):
    def __init__(self, ft_model):
        self.ft_model = ft_model

    def gen_valid_one(self, valid_sure=True):
        while True:
            can = self.ft_model.genRandomTree()
            if not valid_sure or self.ft_model.ok(can):
                break

        return can


def get_hof(name, obj_num, nums):
    fm = FeatureModel(name, num_of_attached_objs=obj_num-2)
    bd = BruteDiscoverer(fm)
    e = set()
    for i in range(nums):
        can = bd.gen_valid_one(valid_sure=False)
        fm.eval(can)
        e.add(tuple(can.fitness))
        if i % 1000 == 0:
            es = list(e)
            es = map(list, es)
            from tools.pareto import eps_sort
            with open(PROJECT_PATH+'/input/'+name+'/'+str(obj_num)+'_objs.hof', 'w') as f:
                front = eps_sort(es)
                pickle.dump(front, f)


def get_hof_all_valid(name, obj_num, nums):
    fm = FeatureModel(name, num_of_attached_objs=obj_num-2)
    bd = BruteDiscoverer(fm)
    e = set()
    for i in range(nums):
        can = bd.gen_valid_one()
        fm.eval(can)
        e.add(tuple(can.fitness))
        if i % 1000 == 0:
            es = list(e)
            es = map(list, es)
            from tools.pareto import eps_sort
            with open(PROJECT_PATH+'/input/'+name+'/'+str(obj_num)+'_objs.validhof', 'w') as f:
                front = eps_sort(es)
                pickle.dump(front, f)

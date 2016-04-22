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
import pickle
import time

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_path = filter(lambda x: x.endswith('SPL'), sys.path)[0]
from tools.hv import HyperVolume


def hv(front, obj_num):
    reference_point = [1] * obj_num
    hv = HyperVolume(reference_point)
    return hv.compute(front)


def valids(individual_objs):
    uniques = set(map(tuple, individual_objs))
    n = len(uniques)
    valid = len([1 for i in uniques if i[1] == 0])
    return n, round(valid / n, 3)


def timestamp(p, t=0):
    return time.time() - t


def pickle_results(model_name, alg_name, pop, logbook):
    pop_file_name = '{0}/Records/{1}_{2}_{3}.pop'.format(project_path, alg_name, model_name, time.strftime('%m%d%y'))
    log_file_name = '{0}/Records/{1}_{2}_{3}.logbook'.format(project_path, alg_name, model_name, time.strftime('%m%d%y'))

    with open(pop_file_name, 'wb') as f:
        pickle.dump(pop, f)

    with open(log_file_name, 'wb') as f:
        pickle.dump(logbook, f)

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
import pdb

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universe import PROJECT_PATH
from tools.result_stat import Stat
from FeatureModel.SPLOT_dict import splot_dict
from deap.tools import *

algorithms = ['NSGA2-SIP', 'SPEA2-SIP', 'SPEA2', 'IBEA', 'NSGA2', 'IBEA-SIP']


def drawing_hv(name):
    def hv(log_books, alg):
        return log_books[alg][-1]['hv|spread|igd|frontier#|valid#'][0]

    hvs = []
    for alg in algorithms:
        hh = [alg]
        for repeat in range(1, 31):
            with open("{0}/Records/exp3/{1}.{2}.logbooks".format(PROJECT_PATH, name, repeat), 'r') as f:
                logbooks = pickle.load(f)
                x = hv(logbooks, alg)
                hh.append(x)
        hvs.append(hh)
    print 'hypervolume:'
    Stat.rdivDemo(hvs, higherTheBetter=True)
    # pdb.set_trace()


def drawing_spread(name):
    def spread(log_books, alg):
        return log_books[alg][-1]['hv|spread|igd|frontier#|valid#'][1]

    spreads = []
    for alg in algorithms:
        sp = [alg]
        for repeat in range(1, 31):
            with open("{0}/Records/exp3/{1}.{2}.logbooks".format(PROJECT_PATH, name, repeat), 'r') as f:
                logbooks = pickle.load(f)
                x = spread(logbooks, alg)
                if x == 0.0:
                    x = 1
                sp.append(x)
        spreads.append(sp)

    print 'Spread:'
    Stat.rdivDemo(spreads, higherTheBetter=False)
    # pdb.set_trace()


def drawing_igd(name):
    def igd(log_books, alg):
        return log_books[alg][-1]['hv|spread|igd|frontier#|valid#'][2]

    igds = []
    for alg in algorithms:
        ig = [alg]
        for repeat in range(1, 31):
            with open("{0}/Records/exp3/{1}.{2}.logbooks".format(PROJECT_PATH, name, repeat), 'r') as f:
                logbooks = pickle.load(f)
                x = igd(logbooks, alg)
                if x == 0.0:
                    x = 1
                ig.append(x)
        igds.append(ig)

    print 'IGD:'
    Stat.rdivDemo(igds, higherTheBetter=False)
    # pdb.set_trace()


def drawing_runtime(name):
    def runtime(log_books, alg):
        return log_books[alg][-1]['timestamp']

    rts = []
    for alg in algorithms:
        rt = [alg]
        for repeat in range(1, 31):
            with open("{0}/Records/exp3/{1}.{2}.logbooks".format(PROJECT_PATH, name, repeat), 'r') as f:
                logbooks = pickle.load(f)
                x = runtime(logbooks, alg)
                rt.append(x)
        rts.append(rt)

    print 'Runtime:'
    Stat.rdivDemo(rts,higherTheBetter=False)


for i in range(8):
    name = splot_dict[i]
    print 'model: ' + name
    drawing_hv(name)
    drawing_spread(name)
    drawing_igd(name)
    drawing_runtime(name)
    print
    print
    print
    print '----'

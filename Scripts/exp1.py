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


"""
Experiment 1 on May 10
Model: webportal, eshop
Objectives dimension: 5
Algorithms: (IBEA, SPEA2, NSGA2) * (1, SIP, penaltyControl)
"""

from FeatureModel.FeatureModel import FeatureModel, FTModelNovelRep
from DEAP_EA import IbeaDiscover, Nsga2Discover, Spea2Discover
from deap import base, creator, tools
import pdb

model_names = [ 'eshop']

for name in model_names:
    for dis in [IbeaDiscover.IbeaDiscover, Nsga2Discover.Nsga2Discover, Spea2Discover.Spea2Discover]:
        model_org = FeatureModel(name)
        model_nc = FTModelNovelRep(name)

        pop, logbook = dis(model_org).run()
        pdb.set_trace()
        pop, logbook = dis(model_nc).run(one_puls_n=True)
        pdb.set_trace()
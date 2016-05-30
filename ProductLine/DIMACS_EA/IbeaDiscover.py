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


from __future__ import print_function
from __future__ import division

import sys
from deap import tools, algorithms
from deap.algorithms import varAnd
from ProductLine.DimacsModel import DimacsModel
from ProductLine.DIMACS_EA.EADiscover import EADiscover
from DEAP_Component.IbeaSelc import selIBEAEnvironment
import pdb

sys.dont_write_bytecode = True


class IbeaDiscover(EADiscover):
    def __init__(self, feature_model):
        super(IbeaDiscover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxOnePoint)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        self.toolbox.register("select", selIBEAEnvironment)
        self.alg_name = 'IBEA'

    @property
    def run(self):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)

        pop, logbook = algorithms.eaAlphaMuPlusLambda(pop, toolbox,
                                       MU, None, CXPB, 1.0 - CXPB, NGEN, self.stats)
        print(max([i[-1] for i in (logbook.select('hv|spread|igd|frontier#|valid#'))]))
        return pop, logbook


def experiment():
    name = "webportal"
    ed = IbeaDiscover(DimacsModel(name))
    pop, logbook = ed.run
    pdb.set_trace()

if __name__ == '__main__':
    import debug
    experiment()

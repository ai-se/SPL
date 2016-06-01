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
import random
from deap import tools
from ProductLine.DimacsModel import DimacsModel
from ProductLine.DIMACS_EA.EADiscover import EADiscover
from DEAP_Component import MoeadSelc
import pdb

sys.dont_write_bytecode = True


class MoeadDiscover(EADiscover):
    def __init__(self, dimacs_model):
        super(MoeadDiscover, self).__init__(dimacs_model, stat_record_valid_only=True)

        self.toolbox.register(
            "mate",
            MoeadSelc.cxSimulatedBinary)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate)

        self.alg_name = 'MOEAD'

    @property
    def run(self):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)
        self.record(pop, 0, evals)

        MoeadSelc.setup(len(self.model.obj), pop, 20)

        for gen in range(1, NGEN):
            evals = 0
            prioritized_select = []
            secondary = pop

            for point_id in MoeadSelc.shuffle(range(len(secondary))):
                child = toolbox.mate(secondary[point_id], pop, CXPB=CXPB)  # crossover
                toolbox.mutate(child)  # mutant

                if not child.fitness.valid:
                    evals += 1
                    toolbox.evaluate(child)  # re-evaluate the mutant

                MoeadSelc.update_neighbors(secondary[point_id], child, secondary)

            pop = prioritized_select + secondary

            if gen % 100 == 0:
                self.record(pop, gen, evals)

        return pop, self.logbook


def experiment():
    name = "webportal"
    model = DimacsModel(name, reducedDec=True)
    ed = MoeadDiscover(model)
    pop, logbook = ed.run

if __name__ == '__main__':
    experiment()

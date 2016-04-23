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

from FeatureModel.ftmodel import FTModel
from DEAP_EA.DEAP_tools.EADiscover import EADiscover
from DEAP_EA.DEAP_tools import MoeadSelc
import DEAP_tools.stat_parts as stat_parts


class MoeadDiscover(EADiscover):
    def __init__(self, feature_model):
        super(MoeadDiscover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            MoeadSelc.cxSimulatedBinary,
            CXPB=0.4)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=0.6)

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = 50
        MU = 1000

        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        MoeadSelc.setup(self.ft.objNum, pop, 20)

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)

        for gen in range(1, NGEN):
            evals = 0
            for point_id in MoeadSelc.shuffle(range(MU)):
                child = toolbox.mate(pop[point_id], pop)  # crossover
                toolbox.mutate(child)  # mutant

                if not child.fitness.valid:
                    evals += 1
                    child.fitness.values, child.fitness.correct = toolbox.evaluate(child)  # re-evaluate the mutant

                MoeadSelc.update_neighbors(pop[point_id], child, pop)

            record = stats.compile(pop)
            logbook.record(gen=gen, evals=evals, **record)
            print(logbook.stream)

        stat_parts.pickle_results(self.ft.name, 'MOEAd', pop, logbook)

        return pop, logbook


def demo():
    ed = MoeadDiscover(FTModel('webportal'))
    pop, logbook = ed.run()

if __name__ == '__main__':
    demo()

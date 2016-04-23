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

from deap import tools
from deap.algorithms import varAnd
from FeatureModel.ftmodel import FTModel
from EADiscover import EADiscover
import DEAP_tools.stat_parts as stat_parts
import pdb


class IbeaDiscover(EADiscover):
    def __init__(self, feature_model):
        super(IbeaDiscover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bin_mutate,
            mutate_rate=0.15)

        self.toolbox.register("select", tools.selIBEA)

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = 50
        MU = 1000
        CXPB = 0.9

        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)

        parents = pop[:]

        # Begin the generational process
        for gen in range(1, NGEN):
            # Vary the parents
            offspring = varAnd(parents, toolbox, CXPB, MU)

            pop[:] = parents + offspring

            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            # Update the hall of fame with the generated individuals
            if hasattr(self, 'halloffame'):
                self.halloffame.update(offspring)

            # Select the next generation parents
            parents[:] = toolbox.select(pop, MU)

            # Update the statistics with the new population
            record = stats.compile(pop) if stats is not None else {}
            logbook.record(gen=gen, evals=evals, **record)

            print logbook.stream

        stat_parts.pickle_results(self.ft.name, 'IBEA', pop, logbook)

        return pop, logbook


def demo():
    ed = IbeaDiscover(FTModel(sys.argv[1]))
    pop, logbook = ed.run()

    pdb.set_trace()

if __name__ == '__main__':
    demo()

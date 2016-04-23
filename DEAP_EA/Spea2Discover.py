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
from FeatureModel.ftmodel import FTModel
from EADiscover import EADiscover
import DEAP_tools.stat_parts as stat_parts
import random
import pdb


class Spea2Discover(EADiscover):
    def __init__(self, feature_model):
        super(Spea2Discover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bin_mutate,
            mutate_rate=0.15)

        self.toolbox.register("select", tools.selSPEA2)

        self.toolbox.register("selectTournament", tools.selTournament, tournsize=2)

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = 50
        MU = 1000
        MuR = 0.06  # mutate rate
        NBAR = 40  # archive size

        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)

        archive = []
        for gen in range(1, NGEN):
            # environmental selection
            archive = toolbox.select(pop + archive, k=NBAR)
            _, evals1 = self.evaluate_pop(archive)  # Evaluate the archive with an invalid fitness

            # mating selection
            mating_pool = toolbox.selectTournament(archive, k=MU)
            offspring_pool = map(toolbox.clone, mating_pool)

            # variation
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

            for mutant in offspring_pool:
                if random.random() < MuR:
                    toolbox.mutate(mutant)

            pop = offspring_pool
            _, evals2 = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness
            record = stats.compile(pop)
            logbook.record(gen=gen, evals=evals1 + evals2, **record)

            print(logbook.stream)

        stat_parts.pickle_results(self.ft.name, 'SPEA-II', pop, logbook)

        return pop, logbook


def demo():
    ed = Spea2Discover(FTModel(sys.argv[1]))
    pop, logbook = ed.run()

    pdb.set_trace()

if __name__ == '__main__':
    demo()

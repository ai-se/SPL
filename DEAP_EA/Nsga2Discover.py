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


class Nsga2Discover(EADiscover):
    def __init__(self, feature_model):
        super(Nsga2Discover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bin_mutate,
            mutate_rate=0.15)

        self.toolbox.register("select", tools.selNSGA2)

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

        for gen in range(1, NGEN):
            # vary the population
            tools.emo.assignCrowdingDist(pop)
            offspring = tools.selTournamentDCD(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]

            for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
                if random.random() <= CXPB:
                    toolbox.mate(ind1, ind2)

                toolbox.mutate(ind1)
                toolbox.mutate(ind2)
                del ind1.fitness.values, ind2.fitness.values

            _, evals = self.evaluate_pop(offspring)   # Evaluate the offspring with an invalid fitness

            # Select the next generation population
            pop = toolbox.select(pop + offspring, MU)
            record = stats.compile(pop)
            logbook.record(gen=gen, evals=evals, **record)
            print(logbook.stream)

        stat_parts.pickle_results(self.ft.name, 'NSGA2', pop, logbook)

        return pop, logbook


def demo():
    from FeatureModel.SPLOT_dict import splot_dict
    ed = Nsga2Discover(FTModel(splot_dict[0]))
    pop, logbook = ed.run()

    pdb.set_trace()

if __name__ == '__main__':
    try:
        demo()
    except:
        import traceback
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

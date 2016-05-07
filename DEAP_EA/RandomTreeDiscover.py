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
from operator import itemgetter
import os.path
import sys

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deap import tools, creator, base
from deap.algorithms import varAnd
from FeatureModel.FeatureModel import FeatureModel, FTModelNovelRep
from DEAP_tools.EADiscover import EADiscover
from DEAP_tools import stat_parts
import pdb


class RandomTreeDiscover(EADiscover):
    def __init__(self, feature_model, stat_record_valid_only=False):
        super(RandomTreeDiscover, self).__init__(feature_model, stat_record_valid_only)
        toolbox = self.toolbox
        toolbox.unregister("individual")
        toolbox.register("individual", lambda: self.creator.Individual(self.ft.genRandomTree().decs))

        toolbox.unregister("population")
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register(
            "mate",
            tools.cxTwoPoint)

        toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        toolbox.register("select", tools.selIBEA)

    def refresh_con_obj(self, pop):
        def set_con_obj(inidvidual, value):
            x = list(inidvidual.fitness.values)
            x[1] = value
            inidvidual.fitness.values = tuple(x)

        tmp_list = []
        for i in pop:
            tmp_list.extend(i.fitness.vioCons)
        count_list = [tmp_list.count(i) for i in range(len(self.ft.ft.con))]
        s = sum(count_list)
        weight_list = [i/s for i in count_list]

        for i in pop:
            l = i.fitness.vioCons

            if len(l) == 0:
                continue

            if len(l) == 1:
                set_con_obj(i, weight_list[l[0]])
            else:
                set_con_obj(i, sum(itemgetter(*l)(weight_list)))

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness
        self.refresh_con_obj(pop)

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)
        # pdb.set_trace()
        parents = pop[:]

        # Begin the generational process
        for gen in range(1, NGEN):
            # pdb.set_trace()
            # Vary the parents
            offspring = varAnd(parents, toolbox, CXPB, MU)

            pop[:] = parents + offspring

            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness
            self.refresh_con_obj(pop)

            # Select the next generation parents
            parents[:] = toolbox.select(pop, MU)

            # Update the statistics with the new population
            if gen % 1 == 0:
                record = stats.compile(parents) if stats is not None else {}
                logbook.record(gen=gen, evals=evals, **record)

                print logbook.stream

            # # early termination control
            # if len(hof) > 290 and gen > 5000:
            #     break
            if 'last_record_time' not in locals():
                last_record_time = 0
            if logbook[-1]['timestamp'] - last_record_time > 600:  # record the logbook every 10 mins
                last_record_time = logbook[-1]['timestamp']
                stat_parts.pickle_results(self.ft.name, 'IBEA', parents, logbook)

        stat_parts.pickle_results(self.ft.name, 'IBEA', parents, logbook)
        return pop, logbook


def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = RandomTreeDiscover(FTModelNovelRep(name))
    # ed = RandomTreeDiscover(FeatureModel(name), stat_record_valid_only=False)
    ed.run()

if __name__ == '__main__':
    import debug
    experiment()

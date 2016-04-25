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

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spl_address = [i for i in sys.path if i.endswith('/SPL')][0]

from deap import tools
from deap.algorithms import varAnd
from FeatureModel.ftmodel import FTModel
from DEAP_EA.DEAP_tools.EADiscover import EADiscover
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
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        self.toolbox.register("select", tools.selIBEA)

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        hof = tools.HallOfFame(300)
        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)
        # pdb.set_trace()
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

            # correct_pop = [p for p in pop if p.fitness.correct]
            # if correct_pop:
            #     hof.update(correct_pop)
            hof.update(pop)

            # Update the statistics with the new population
            if gen % 100 == 0:
                record = stats.compile(pop) if stats is not None else {}
                logbook.record(gen=gen, evals=evals, **record)

                print logbook.stream

                with open(spl_address+'/Records/'+self.ft.name+'.hof', 'w') as f:
                    pickle.dump(hof, f)

            if len(hof) > 290 and gen > 5000:
                break

        stat_parts.pickle_results(self.ft.name, 'IBEA', pop, logbook)

        return pop, logbook


def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = IbeaDiscover(FTModel(name))
    pop, logbook = ed.run()


def record_hof():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = IbeaDiscover(FTModel(name))
    pop, logbook = ed.run()


def load_dump_hof():
    from FeatureModel.SPLOT_dict import splot_dict
    for i in range(10):
        name = splot_dict[i]
        ed = IbeaDiscover(FTModel(name))
        with open(spl_address+'/input/hof_ibea/'+name+'.hof', 'r') as f:
            hh = pickle.load(f)

        if len(hh) == 0:
            continue

        with open(spl_address+'/input/'+name+'.correctpf', 'w') as f:
            correct_pf = map(list,[h.fitness.values for h in hh])
            pickle.dump(correct_pf, f)


if __name__ == '__main__':
    experiment()

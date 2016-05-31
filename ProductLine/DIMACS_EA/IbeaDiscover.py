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
from ProductLine.DimacsModel import DimacsModel
from ProductLine.DIMACS_EA.EADiscover import EADiscover
from DEAP_Component.IbeaSelc import selIBEAEnvironment
from DEAP_Component.stat_parts import true_candidate_collector
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

    @staticmethod
    def eaAlphaMuPlusLambda(population, toolbox, mu, _,
                            cxpb, mutpb, ngen, stats=None, halloffame=None,
                            verbose=__debug__):

        """This is the :math:`(~\alpha,\mu~,~\lambda)` evolutionary algorithm."""
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

        parents = population[:]

        # Begin the generational process
        for gen in range(1, ngen + 1):
            # Vary the parents
            if hasattr(toolbox, 'variate'):
                offspring = toolbox.variate(parents, toolbox, cxpb, mutpb)
            else:
                offspring = algorithms.varAnd(parents, toolbox, cxpb, mutpb)

            population[:] = parents + offspring

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            for rr in offspring: # TODO emergency bug!!
                if not hasattr(rr.fitness, 'correct') and rr in invalid_ind:
                    pdb.set_trace()

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Select the next generation parents
            parents[:] = toolbox.select(population, mu)

            # Update the statistics with the new population
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                print(logbook.stream)
        return population, logbook

    @property
    def run(self):
        toolbox = self.toolbox
        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)

        pop, logbook = self.eaAlphaMuPlusLambda(pop, toolbox,
                                       MU, None, CXPB, 1.0 - CXPB, NGEN, self.stats)
        true_candidate_collector(self.model.name, pop)
        return pop, logbook


def experiment():
    name = "webportal"
    model = DimacsModel(name, reducedDec=True)
    ed = IbeaDiscover(model)
    pop, logbook = ed.run
    pdb.set_trace()

if __name__ == '__main__':
    import debug
    experiment()

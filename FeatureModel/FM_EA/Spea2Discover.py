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

import sys
from deap import tools
from FeatureModel.FeatureModel import FTModelNovelRep
from FeatureModel.FM_EA import EADiscover
import random

sys.dont_write_btyecode = True


class Spea2Discover(EADiscover):
    def __init__(self, feature_model):
        super(Spea2Discover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        self.toolbox.register("env_select", tools.selSPEA2)

        self.toolbox.register("mate_select", self.binary_tournament_selc)

        self.alg_name = 'SPEA2'

    def run(self, record_hof=False, sip=False):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        NBAR = self.ea_configurations['SPEAII_archive_size']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness
        self.record(pop, 0, evals, record_hof)

        archive = []
        for gen in range(1, NGEN):
            # print gen

            # environmental selection
            if sip:
                archive = self.one_plus_n_engine(pop+archive, NBAR, toolbox.env_select)
            else:
                archive = toolbox.env_select(pop + archive, k=NBAR)

            _, evals1 = self.evaluate_pop(archive)  # Evaluate the archive with an invalid fitness

            # mating selection
            mating_pool = toolbox.mate_select(archive, MU, sip)
            offspring_pool = map(toolbox.clone, mating_pool)

            # variation
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

            for mutant in offspring_pool:
                if random.random() < 0.4:
                    toolbox.mutate(mutant)

            pop = offspring_pool
            _, evals2 = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            self.record(archive, gen, evals1+evals2, record_hof)

        # stat_parts.pickle_results(self.ft.name, self.alg_name, archive, self.logbook)

        return pop, self.logbook


class Spea2DiscoverSIP(Spea2Discover):
    def __init__(self, feature_model):
        if type(feature_model) is not FTModelNovelRep:
            feature_model = FTModelNovelRep(feature_model.name)
        super(Spea2DiscoverSIP, self).__init__(feature_model)
        self.alg_name = "SPEA2-SIP"

    def run(self, record_hof=False, sip=True):
        return super(Spea2DiscoverSIP, self).run(record_hof, sip=True)


def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = Spea2Discover(FTModelNovelRep(name, 4),)
    pop, logbook = ed.run(sip=True)

if __name__ == '__main__':
    experiment()

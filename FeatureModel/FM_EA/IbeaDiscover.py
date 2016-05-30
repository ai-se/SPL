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

from deap import tools
from deap.algorithms import varAnd
from FeatureModel.FeatureModel import FTModelNovelRep, FeatureModel
from FeatureModel.FM_EA.EADiscover import EADiscover
from DEAP_Component.IbeaSelc import selIBEAEnvironment
import DEAP_Component.stat_parts as stat_parts
import pdb
import sys

sys.dont_write_btyecode = True


class IbeaDiscover(EADiscover):
    def __init__(self, feature_model):
        super(IbeaDiscover, self).__init__(feature_model=feature_model)

        self.toolbox.register(
            "mate",
            tools.cxOnePoint)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        self.toolbox.register("en_selc", selIBEAEnvironment)
        self.toolbox.register("mat_selc", self.binary_tournament_selc)
        self.alg_name = 'IBEA'

    def run(self):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)

        for gen in range(1, NGEN):
            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            # environmental selection
            parents = toolbox.en_selc(pop, MU)
            self.record(parents, gen, evals)

            if gen == NGEN - 1:
                pop = parents
                return pop, self.logbook

            mating = toolbox.mat_selc(parents, int(MU))

            # Vary the parents
            offspring = varAnd(mating, toolbox, CXPB, MU)
            pop = parents + offspring


# class IbeaDiscoverSIP(IbeaDiscover):
#     def __init__(self, feature_model):
#         if type(feature_model) is not FTModelNovelRep:
#             feature_model = FTModelNovelRep(feature_model.name)
#         super(IbeaDiscoverSIP, self).__init__(feature_model)
#         self.alg_name = 'IBEA-SIP'
#
#     def run(self, record_hof=False, sip=True):
#         return super(IbeaDiscoverSIP, self).run(record_hof, sip=True)


def experiment():
    from FeatureModel.SPLOT_dict import first_argv_name
    name = first_argv_name()
    print(name)
    # ed = IbeaDiscoverSIP(FTModelNovelRep(name))
    ed = IbeaDiscover(FeatureModel(name))
    pop, logbook = ed.run()
    stat_parts.true_candidate_collector(name, pop)


if __name__ == '__main__':
    experiment()

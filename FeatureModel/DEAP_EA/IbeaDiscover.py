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
spl_address = [i for i in sys.path if i.endswith('/SPL')][0]

from deap import tools
from deap.algorithms import varAnd
from FeatureModel.FeatureModel import FTModelNovelRep
from FeatureModel.DEAP_EA.DEAP_tools import EADiscover
from DEAP_tools.IbeaSelc import selIBEAEnvironment
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

        self.toolbox.register("en_selc", selIBEAEnvironment)
        self.toolbox.register("mat_selc", self.binary_tournament_selc)
        self.alg_name = 'IBEA'

    def run(self, record_hof=False, sip=False):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)
        self.record(pop, 0, evals, record_hof)

        parents = pop

        for gen in range(1, NGEN):
            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            # environmental selection
            if sip:
                parents = self.one_plus_n_engine(pop, MU, toolbox.en_selc)
            else:
                parents = toolbox.en_selc(pop, MU)
            self.record(parents, gen, evals, record_hof)

            mating = toolbox.mat_selc(parents, int(MU), sip)
            # pdb.set_trace()
            # Vary the parents
            offspring = varAnd(mating, toolbox, CXPB, MU)
            pop = parents + offspring

        # stat_parts.pickle_results(self.ft.name, self.alg_name, parents, self.logbook)
        return pop, self.logbook


class IbeaDiscoverSIP(IbeaDiscover):
    def __init__(self, feature_model):
        if type(feature_model) is not FTModelNovelRep:
            feature_model = FTModelNovelRep(feature_model.name)
        super(IbeaDiscoverSIP, self).__init__(feature_model)
        self.alg_name = 'IBEA-SIP'

    def run(self, record_hof=False, sip=True):
        return super(IbeaDiscoverSIP, self).run(record_hof, sip=True)


def experiment():
    from FeatureModel.SPLOT_dict import first_argv_name
    name = first_argv_name()
    ed = IbeaDiscoverSIP(FTModelNovelRep(name))
    pdb.set_trace()
    # ed = IbeaDiscover(FeatureModel(name))
    pop, logbook = ed.run()


if __name__ == '__main__':
    experiment()

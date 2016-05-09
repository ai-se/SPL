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
from FeatureModel.FeatureModel import FeatureModel, FTModelNovelRep
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

        self.alg_name = 'IBEA'

    def run(self, record_hof=False, one_puls_n=False):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)
        self.record(pop, 0,evals, record_hof)

        parents = pop

        for gen in range(1, NGEN):
            # Vary the parents
            offspring = varAnd(parents, toolbox, CXPB, MU)

            pop = parents + offspring

            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            # environmental selection
            if one_puls_n:
                parents = self.one_plus_n_engine(pop, MU, toolbox.select)
            else:
                parents = toolbox.select(pop, MU)

            self.record(parents, gen, evals, record_hof)

        stat_parts.pickle_results(self.ft.name, self.alg_name, parents, self.logbook)
        return pop, self.logbook


# def run_with_hof():
#     from FeatureModel.SPLOT_dict import splot_dict
#     name = splot_dict[int(sys.argv[1])]
#     ed = IbeaDiscover(FeatureModel(name))
#     pop, logbook = ed.run(record_hof=False)
#
#
# def load_dump_hof():
#     from FeatureModel.SPLOT_dict import splot_dict
#     for i in range(10):
#         name = splot_dict[i]
#         ed = IbeaDiscover(FeatureModel(name))
#         with open(spl_address+'/input/hof_ibea/'+name+'.hof', 'r') as f:
#             hh = pickle.load(f)
#
#         if len(hh) == 0:
#             continue
#
#         with open(spl_address+'/input/'+name+'.pf', 'w') as f:
#             correct_pf = map(list,[h.fitness.values for h in hh])
#             pickle.dump(correct_pf, f)


def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    pdb.set_trace()
    ed = IbeaDiscover(FTModelNovelRep(name))
    pop, logbook = ed.run(one_puls_n=True)

    # ed = IbeaDiscover(FeatureModel(name))
    # pop, logbook = ed.run(one_puls_n=False)


if __name__ == '__main__':
    import debug
    experiment()

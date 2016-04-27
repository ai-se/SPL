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
import pdb
import random

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spl_address = [i for i in sys.path if i.endswith('/SPL')][0]

from FeatureModel.ftmodel import FTModel
from MSDiscover import MSDiscover
from deap import tools, creator
import DEAP_tools.stat_parts as stat_parts


class MSEngine4(MSDiscover):
    @staticmethod
    def swap(s1, s2):
        tmp = s1
        s1 = s2
        s2 = tmp
        return s1, s2

    def cxGP(self, ind1, ind2, sub_root):
        h = hash(sub_root.id)
        if h not in self.subtree_dict:
            self.subtree_dict[h] = sorted(self.thetree.get_subtree_index(sub_root))
        indices = self.subtree_dict[h]
        del ind1.fitness.values
        del ind2.fitness.values
        for i in indices:
            ind2[i], ind1[i] = self.swap(ind1[i], ind2[i])
        return ind1, ind2

    def gen_one_individual(self):
        return creator.Individual(self.ft.genRandomTree().decs)

    def __init__(self, feature_model):
        super(MSEngine4, self).__init__(feature_model)

        self.subtree_dict = dict()
        self.cons = self.ft.ft.con
        self.thetree = self.ft.ft
        self.toolbox.register(
            "mate",
            self.cxGP
        )

        self.toolbox.register(
            "population",
            tools.initRepeat,
            list,
            self.gen_one_individual)

    def run(self, record_hof=False):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = self.ms_configurations['NGEN']
        MU = self.ms_configurations['MU']
        CXPB = self.ms_configurations['CXPB']
        MT = self.ms_configurations['MatingThreshold']

        if record_hof:
            hof = tools.HallOfFame

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)

        for gen in range(1, NGEN):
            # the individual violated constraint indices dict
            VIO = []
            for can_i, can in enumerate(pop):
                vio = []  # record the current candidate
                for con_i, constraint in enumerate(self.cons):
                    if constraint.is_violated(self.thetree, can):
                        vio.append(con_i)
                VIO.append(vio)
            VIO = map(set, VIO)

            # mating
            """
            to balance the efficiency and valid rate. Only mate the worse MatingThreshold(e.g. 15%)
            """
            sorted_vio = sorted(VIO, key=len, reverse=True)
            high_vio = sorted_vio[:int(len(VIO) * MT)]
            from operator import itemgetter
            for i in high_vio:
                if not i:
                    break
                # high_vio[j] intersets with i has the min len
                j, _ = min(enumerate([i & h for h in high_vio]), key=itemgetter(1))

                # try to mate high_vio[i] and high_vio[j]
                index1 = VIO.index(i)
                index2 = VIO.index(high_vio[j])
                while True:
                    sr = random.choice(list(VIO[index1] | VIO[index2] - VIO[index1] & VIO[index2]))
                    if pop[index1][sr] == pop[index2][sr]:
                        break
                pop[index1], pop[index2] = \
                    toolbox.mate(pop[index1], pop[index2], self.thetree.features[sr])
                # literals = []
                # for x_con in VIO[index1] | VIO[index2]-VIO[index1] & VIO[index2]:
                #     literals.extend(self.cons[x_con].literals)
                # pdb.set_trace()
                # for l in literals:
                #     index = self.thetree.find_fea_index(l)
                #     if pop[index1][index] == pop[index2][index]:
                #         pdb.set_trace()
                #         pop[index1], pop[index2] = \
                #             toolbox.mate(pop[index1], pop[index2], self.thetree.features[index])
                # pdb.set_trace()
            _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

            record = stats.compile(pop)
            logbook.record(gen=0, evals=evals, **record)
            print(logbook.stream)
            # pdb.set_trace()


        return 1

def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = MSEngine4(FTModel(name))
    ed.run()

if __name__ == '__main__':
    import debug
    experiment()
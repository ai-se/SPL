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

from deap import base, creator, tools, algorithms
from deap.benchmarks.tools import hypervolume
from FeatureModel.ftmodel import FTModel
from FeatureModel.discoverer import Discoverer
from GALE.model import *
import DEAP_tools.stat_parts as stat_parts
import time
import random
import pickle
import pdb


class IbeaDiscover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            self.ft = FTModel(name, num_of_attached_objs=len(feature_model) - 2, setConVioAsObj=True)
        else:
            self.ft = feature_model

        creator.create("EqWeiFitnessMin", base.Fitness, weights=[-1.0] * self.ft.objNum)
        creator.create("Individual", list, fitness=creator.EqWeiFitnessMin)

        toolbox = base.Toolbox()

        toolbox.register("randBin", lambda: int(random.choice([0, 1])))
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.randBin, n=self.ft.decNum)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.eval_func)

        toolbox.register(
            "mate",
            tools.cxTwoPoint)

        toolbox.register(
            "mutate",
            self.bin_mutate,
            mutate_rate=0.15)

        toolbox.register("select", tools.selIBEA)

        self.toolbox = toolbox

    def gen_valid_one(self):
        assert False, "Do not use this function. Function not provided at this time."
        pass

    def eval_func(self, dec_l):
        candidate = o(decs=dec_l)
        self.ft.eval(candidate)
        return tuple(candidate.scores)

    @staticmethod
    def bin_mutate(individual, mutate_rate):
        for i in xrange(len(individual)):
            if random.random() < mutate_rate:
                individual[i] = 1 - individual[i]
        return individual

    def run(self):
        toolbox = self.toolbox

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("valid_rate", stat_parts.valid_rate)
        stats.register("hv", stat_parts.hv, obj_num=self.ft.objNum)
        stats.register("timestamp", stat_parts.timestamp, t=time.time())

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "valid_rate", "hv", "timestamp"

        NGEN = 50
        MU = 1000
        CXPB = 0.9

        pop = toolbox.population(n=MU)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        record = stats.compile(pop)
        logbook.record(gen=0, evals=len(invalid_ind), **record)
        print(logbook.stream)
        algorithms.eaAlphaMuPlusLambda(pop, toolbox,
                                       MU, None, CXPB, 1.0 - CXPB, NGEN, stats)

        print("Final population hypervolume is %f" % hypervolume(pop, [1] * self.ft.objNum))

        return pop, logbook


def demo():
    ed = IbeaDiscover(FTModel(sys.argv[1]))
    pop, logbook = ed.run()

    with open('pop_ibda_' + sys.argv[1], 'wb') as f:
        pickle.dump(pop, f)

    pdb.set_trace()

if __name__ == '__main__':
    demo()

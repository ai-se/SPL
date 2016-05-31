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
from deap import base, creator, tools
from ProductLine.DimacsModel import DimacsModel
from ProductLine.discoverer import Discoverer
from model import *
import DEAP_Component.stat_parts as stat_parts
import time
import random
import pdb

sys.dont_write_btyecode = True


# TODO unit testing

class EADiscover(Discoverer):
    def __init__(self, dimacs_model, stat_record_valid_only=True):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in dimacs_model.obj]:
            name = dimacs_model.name
            self.model = DimacsModel(name, num_of_attached_objs=len(dimacs_model.obj) - 2, add_con_vio_to_objs=True)
        else:
            self.model = dimacs_model

        creator.create("FitnessMin", base.Fitness, weights=[-1.0] * self.model.objNum, correct=bool)
        creator.create("Individual", list, fitness=creator.FitnessMin, fulfill=list)

        toolbox = base.Toolbox()

        toolbox.register("randBin", lambda: int(random.choice([0, 1])))
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.randBin, n=self.model.decNum)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.eval_func)

        stats = tools.Statistics(lambda ind: ind)

        stats.register("hv|spread|igd|frontier#|valid#",
                       stat_parts.stat_basing_on_pop,
                       record_valid_only=stat_record_valid_only)

        stats.register("timestamp", stat_parts.timestamp, t=time.time())

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "hv|spread|igd|frontier#|valid#", "timestamp"

        self.creator = creator
        self.toolbox = toolbox
        self.stats = stats
        self.logbook = logbook
        self.hof = tools.HallOfFame(300)  # in case we need it

        self.ea_configurations = {
            'NGEN': 500,
            'MU': 100,
            'CXPB': 0.9,
            'MutateRate': 0.05,
            'SPEAII_archive_size': 100
        }

    def set_ea_gen(self, ngen):
        self.ea_configurations['NGEN'] = ngen

    def gen_valid_one(self):
        assert False, "Do not use this function. Function not provided at this time."
        pass

    def eval_func(self, ind):
        can = o(decs=ind)
        self.model.eval(can)
        ind.fulfill = can.fulfill
        ind.fitness.conVio = can.conVio
        ind.fitness.correct = self.model.ok(can)
        return tuple(can.fitness)

    @staticmethod
    def bit_flip_mutate(individual, mutate_rate):
        for i in range(len(individual)):
            if random.random() < mutate_rate:
                individual[i] = 1 - individual[i]
                del individual.fitness.values
        return individual,

    @staticmethod
    def binary_tournament_selc(population, return_size):
        import random
        parents = []
        for _ in range(return_size):
            # Pick individuals for tournament
            tournament = [random.choice(population) for _ in range(2)]
            # Sort according to fitness
            tournament.sort()
            # Winner is element with smallest fitness
            parents.append(tournament[0])

        return parents

    def evaluate_pop(self, pop):
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        for i in invalid_ind:
            self.eval_func(i)
        return pop, len(invalid_ind)

    def run(self):
        raise NotImplementedError

    def record(self, pop, gen, evals):
        # Update the statistics with the new population
        if gen % 100 == 0:
            record = self.stats.compile(pop)
            self.logbook.record(gen=gen, evals=evals, **record)

            print(self.logbook.stream)
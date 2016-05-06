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

from deap import tools, creator, base
from FeatureModel.FeatureModel import FeatureModel, FTModelNovelRep
from DEAP_tools.EADiscover import EADiscover
import pdb


class RandomTreeDiscover(EADiscover):
    def __init__(self, feature_model):
        super(RandomTreeDiscover, self).__init__(feature_model)
        toolbox = self.toolbox
        toolbox.unregister("individual")
        toolbox.register("individual", lambda: self.creator.Individual(self.ft.genRandomTree().decs))

        toolbox.unregister("population")
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def run(self):
        toolbox = self.toolbox

        init_pop = toolbox.population(n=100)
        self.evaluate_pop(init_pop)
        print [i.fitness.correct_ft for i in init_pop]

        pdb.set_trace()

def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    # ed = RandomTreeDiscover(FTModelNovelRep(name))
    ed = RandomTreeDiscover(FeatureModel(name))
    ed.run()

if __name__ == '__main__':
    import debug
    experiment()
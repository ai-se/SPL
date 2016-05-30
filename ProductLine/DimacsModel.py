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
import dimacs_parser
import sys
import pdb
from universe import PROJECT_PATH, load_appendix, append_attributes
from model import *

sys.dont_write_bytecode = True


class DimacsModel(model):
    def __init__(self, name, num_of_attached_objs=3, add_con_vio_to_objs=True):
        # index in the cnfs are starting at 1!!
        # index in features_names are starting at 0
        self.name = name

        # load url
        url = "{0}/dimacs_data/{1}.dimacs".format(PROJECT_PATH, name)
        self.feature_names, self.featureNum, self.cnfs, self.cnfNum = \
            dimacs_parser.load_product_url(url)

        dec = [Has(l, 0, 1) for l in self.feature_names]
        self.append_value_dict = dict()
        obj = [Has(name='richness', lo=0, hi=self.featureNum, goal=lt)]
        if add_con_vio_to_objs:
            obj.append(Has(name='conVio', lo=0, hi=self.cnfNum, goal=lt))

        attach_attrs = ['familiarity', 'defects', 'cost', 'app1', 'app2', 'app3'][:num_of_attached_objs]
        for a in attach_attrs:
            self.append_value_dict[a] = load_appendix(self.name, self.featureNum, a)
            g = lt if append_attributes[a][1] else gt
            obj.append(Has(name=a, lo=0, hi=sum(self.append_value_dict[a]), goal=g))

        model.__init__(self, dec, obj)

    def __repr__(self):
        return "=====================\n" \
               "Type: DimacsModel\n" \
               "Name: {0}\n" \
               "Feature Number: {1}\n" \
               "Constraints : {2}\n" \
               "=====================\n".format(self.name, self.featureNum, self.cnfNum)

    def check_cnf(self, cnf_id, lst):
        cnf = self.cnfs[cnf_id]
        for i in cnf:
            if (lst[abs(i)-1] > 0) == (i > 0):
                return True
        return False

    def check_lst(self, lst):
        for i in range(self.cnfNum):
            if not self.check_cnf(i, lst):
                return False
        return True

    def find_core_dead_features_cnfs(self):
        """
        :return:
        cores, index start at 0, all core features must be 1
        deads, index start at 0, all dead features must be 0
        trival_cnfs: these cnfs is useless. if all cores be 1 and all deads be 0
        """
        max_cnf_len = max(len(cnf) for cnf in self.cnfs)
        cores = []
        deads = []
        trival_cnfs = []
        for cnf in self.cnfs:
            if len(cnf) == 1:
                if cnf[0] > 0:
                    cores.append(cnf[0]-1)
                else:
                    deads.append(-cnf[0]-1)

        for l in range(2, max_cnf_len+1):
            for cnf in self.cnfs:
                if len(cnf) != l:
                    continue

                flexible = []
                for i in cnf:
                    if abs(i)-1 not in cores+deads:
                        flexible.append(i)
                    elif abs(i)-1 in cores and i > 0:
                        trival_cnfs.append(cnf)
                        break
                    elif abs(i)-1 in deads and i < 0:
                        trival_cnfs.append(cnf)
                        break

                if (cnf not in trival_cnfs) and len(flexible) == 1:
                    if flexible[0] > 0:
                        cores.append(flexible[0]-1)
                    else:
                        deads.append(-flexible[0]-1)
        return cores, deads, trival_cnfs

    def eval(self, candidate, doNorm=True):
        if not hasattr(candidate, "fulfill"):
            fulfill = candidate.decs
        else:
            fulfill = candidate.decs  # TODO
        candidate.fulfill = fulfill

        obj1 = self.featureNum - sum(fulfill)  # LESS IS MORE!
        candidate.fitness = [obj1]

        # cnf violation
        conVio = self.cnfNum
        conViolated_index = []
        for cc_i in range(self.cnfNum):
            if self.check_cnf(cc_i, fulfill):
                conVio -= 1
            else:
                conViolated_index.append(cc_i)

        all_obj_names = [o.name for o in self.obj]
        if 'conVio' in all_obj_names:
            candidate.fitness.append(conVio)
        candidate.conVio = conVio
        candidate.conViolated_index = conViolated_index

        for o_name in all_obj_names:
            if o_name == 'richness' or o_name == 'conVio':
                continue

            total = 0
            for x, f_i in zip(self.append_value_dict[o_name], range(self.featureNum)):
                if fulfill[f_i] == 1:
                    total += x
            if not append_attributes[o_name][1]:  # LESS IS MORE!
                hi = [o.hi for o in self.obj if o.name == o_name][0]
                total = hi - total
            candidate.fitness.append(total)

        if doNorm:
            self.normObjs(candidate)

    def ok(self, c, con_vio_tol=0):
        if not hasattr(c, 'fitness'):
            self.eval(c)
        elif not c.fitness:
            self.eval(c)
        return c.conVio <= con_vio_tol


def demo():
    x = DimacsModel('linux')
    print(x)
    import pycosat
    can = o()
    t = pycosat.solve(x.cnfs)
    t = map(lambda x:int(x>0), t)
    can.decs = t
    x.eval(can)
    pdb.set_trace()
    for i, sol in enumerate(pycosat.itersolve(x.cnfs)):
        print(i)
        if i > 1000:
            break

    a,b,c = x.find_core_dead_features_cnfs()

if __name__ == '__main__':
    demo()

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
import os.path
import sys
import pdb

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DimacsModel(object):
    def __init__(self, name):
        # index in the cnfs are starting at 1!!
        # index in features_names are starting at 0
        from universe import PROJECT_PATH
        url = "{0}/dimacs_data/{1}.dimacs".format(PROJECT_PATH, name)
        self.feature_names, self.featureNum, self.cnfs, self.cnfNum = \
            dimacs_parser.load_product_url(url)

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


def demo():
    x = DimacsModel('simple')
    import pycosat
    for i, sol in enumerate(pycosat.itersolve(x.cnfs)):
        print(sol)
    pdb.set_trace()
    a,b,c = x.find_core_dead_features_cnfs()

if __name__ == '__main__':
    demo()

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
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from universe import PROJECT_PATH as spl_addr
from model import *
from parser import load_ft_url
import pickle
import os
import pdb


maximize = False
minimize = True
append_attributes = {
    'cost': (10, 100, minimize),
    'time': (20, 1000, minimize),
    'familiarity': (5, 10, maximize),
    'app1': (0, 10, minimize),
    'app2': (100, 1000, minimize),
    'app3': (0, 1, minimize),
}


class FeatureModel(model):
    def _load_appendix(self, attr_name):
        subdirectories = os.listdir(spl_addr+'/input')
        if self.name not in subdirectories:
            os.mkdir(spl_addr+'/input/'+self.name)
        data_f = spl_addr + '/input/' + self.name

        try:
            with open(data_f + '/' + attr_name, 'r') as f:
                return pickle.load(f)
        except IOError:  # no such file
            lower, higher, less_is_more = append_attributes[attr_name]
            r = random.uniform if higher - lower < 10 else random.randint
            values = [r(lower, higher) for _ in self.ft.features]
            with open(data_f + '/' + attr_name, 'w') as f:
                pickle.dump(values, f)
            return values

    def __init__(self, name, num_of_attached_objs=4, setConVioAsObj=True):
        self.name = name
        url = spl_addr + '/splot_data/' + self.name + '.xml'
        self.ft = load_ft_url(url)
        self.append_value_dict = dict()

        dec = [Has(l.id, 0, 1) for l in self.ft.features]

        obj = [Has(name='fea', lo=0, hi=self.ft.featureNum, goal=lt)]
        if setConVioAsObj:
            obj.append(Has(name='conVio', lo=0, hi=len(self.ft.con)+1, goal=lt))

        attach_attrs = ['cost', 'time', 'familiarity', 'app1', 'app2', 'app3'][:num_of_attached_objs]
        for a in attach_attrs:
            self.append_value_dict[a] = self._load_appendix(a)
            g = lt if append_attributes[a][2] else gt
            obj.append(Has(name=a, lo=0, hi=sum(self.append_value_dict[a]), goal=g))

        model.__init__(self, dec, obj)

    def __repr__(self):
        s = '---Information for SPL--------\n'
        s += 'Name:%s\n' % self.name
        s += 'Leaves #:%d\n' % len(self.ft.leaves)
        s += 'Total Features #:%d\n' % self.ft.featureNum
        s += 'Constraints#:%d\n' % len(self.ft.con)
        s += '-' * 30
        s += '\n'
        return s

    def eval(self, candidate, doNorm=True, returnFulfill=False, checkTreeStructure=False):
        t = self.ft  # abbr.
        fulfill = candidate.decs

        obj1 = len(t.features) - sum(fulfill)  # LESS IS MORE!
        candidate.fitness = [obj1]

        # constraint violation
        conVio = len(t.con) + 1
        for cc in t.con:
            if cc.is_correct(t, fulfill):
                conVio -= 1

        # another import constraint, the feature tree structure!
        if checkTreeStructure:
            if self.ft.check_fulfill_valid(fulfill):
                candidate.correct_ft = True
                conVio -= 1
            else:
                candidate.correct_ft = False
        else:
            conVio -= 1

        all_obj_names = [o.name for o in self.obj]
        if 'conVio' in all_obj_names:
            candidate.fitness.append(conVio)
        candidate.conVio = conVio

        for o_name in all_obj_names:
            if o_name == 'fea' or o_name == 'conVio':
                continue

            total = 0
            for x, f_i in zip(self.append_value_dict[o_name], range(t.featureNum)):
                if fulfill[f_i] == 1:
                    total += x
            if not append_attributes[o_name][2]:
                hi = [o.hi for o in self.obj if o.name == o_name][0]
                total = hi - total
            candidate.fitness.append(total)

        if doNorm:
            self.normObjs(candidate)

        if returnFulfill:
            return fulfill
        else:
            return None

    """
    checking whether the candidate meets ALL constraints
    """

    def ok(self, c, con_vio_tol=0):
        if not hasattr(c, 'scores'):
            self.eval(c)
        elif not c.fitness:
            self.eval(c)

        if not hasattr(c, 'correct_ft'):
            c.correct_ft = self.ft.check_fulfill_valid(c.decs)

        if not c.correct_ft:
            return False
        else:
            return c.conVio <= con_vio_tol

    def genRandomCan(self, engine_version):
        """
        when engine_version == 'random_sample', then generate any sample regardless the validness.
        """

        if engine_version == 'random_sample':
            engine = self.mutateEngines['brute']
            return engine.gen_valid_one(valid_sure=False)

        engine = self.mutateEngines[engine_version]
        return engine.gen_valid_one()

    def genRandomTree(self):
        """get candidates which meets the tree structure. ignore the constraints"""
        def rand_ones(lstLen, onesNum):
            result = [0] * lstLen
            l = range(lstLen)
            random.shuffle(l)
            for i in l[0:onesNum]:
                result[i] = 1
            return result

        def genNode(node, fulfill):
            checked = fulfill[self.ft.find_fea_index(node)]
            if checked == 0:
                self.ft.fill_subtree_0(node, fulfill)
                return fulfill

            if not node.children:
                return fulfill

            if node.node_type is not 'g':
                for c in node.children:
                    if c.node_type is 'o':
                        fulfill[self.ft.find_fea_index(c)] = random.choice([0,1])
                    else:
                        fulfill[self.ft.find_fea_index(c)] = 1
                child_sum = sum(fulfill[self.ft.find_fea_index(c)] for c in node.children)
                if child_sum == 0:
                    fulfill[self.ft.find_fea_index(random.choice(node.children))] = 1
            else:  # deal with the groups
                s_num = random.randint(node.g_d, node.g_u)
                lst = rand_ones(len(node.children), s_num)
                for l, c in zip(lst, node.children):
                    fulfill[self.ft.find_fea_index(c)] = l

            for c in node.children:
                genNode(c, fulfill)
            return fulfill

        fulfill = [0] * self.decNum
        fulfill[0] = 1
        decs = genNode(self.ft.root, fulfill)
        return o(decs=decs, correct_ft=True)


def demo(name):
    m = FeatureModel(name, setConVioAsObj=True)
    return


if __name__ == '__main__':
    from SPLOT_dict import splot_dict
    for x in range(10):
        name = splot_dict[x]
        demo(name)

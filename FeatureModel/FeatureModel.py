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
from operator import itemgetter
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

    def eval(self, candidate, doNorm=True, returnFulfill=False, checkTreeStructure=False, fulfill=None):
        t = self.ft  # abbr.
        if not fulfill:
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
        if not hasattr(c, 'snoncores'):
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

    def rand_ones(self,lstLen, onesNum):
        result = [0] * lstLen
        l = range(lstLen)
        random.shuffle(l)
        for i in l[0:onesNum]:
            result[i] = 1
        return result

    def genNode(self, node, fulfill):
        checked = fulfill[self.ft.find_fea_index(node)]
        if checked == 0:
            self.ft.fill_subtree_0(node, fulfill)
            return fulfill

        if not node.children:
            return fulfill

        if node.node_type is not 'g':
            for c in node.children:
                if c.node_type is 'o':
                    fulfill[self.ft.find_fea_index(c)] = random.choice([0, 1])
                else:
                    fulfill[self.ft.find_fea_index(c)] = 1
            child_sum = sum(fulfill[self.ft.find_fea_index(c)] for c in node.children)
            if child_sum == 0:
                fulfill[self.ft.find_fea_index(random.choice(node.children))] = 1
        else:  # deal with the groups
            s_num = random.randint(node.g_d, node.g_u)
            lst = self.rand_ones(len(node.children), s_num)
            for l, c in zip(lst, node.children):
                fulfill[self.ft.find_fea_index(c)] = l

        for c in node.children:
            self.genNode(c, fulfill)
        return fulfill

    def genRandomTree(self):
        """get candidates which meets the tree structure. ignore the constraints"""
        fulfill = [0] * self.decNum
        fulfill[0] = 1
        decs = self.genNode(self.ft.root, fulfill)
        return o(decs=decs, correct_ft=True)


class FTModelNovelRep(FeatureModel):
    def coding_func(self):
        ft = self.ft

        # find the must-1 features
        must1 = []
        for feature in ft.features:
            tmp = True
            cursor = feature
            while cursor.parent:
                if cursor.node_type not in ['m', 'r', 'g']:
                    tmp = False
                    break
                cursor = cursor.parent
            if tmp:
                must1.append(feature)

        must1_index = []
        for f_i, f in enumerate(ft.features):
            if f in must1:
                must1_index.append(f_i)

        # get the reasonable features, i.e., at least one of the child are not optional or the feature itself is 'g'
        reasonable = []
        for feature in ft.features:
            if feature in must1:
                continue

            if feature.node_type is 'g':
                reasonable.append(feature)
                continue

            if [c for c in feature.children if c.node_type is not 'o']:
                reasonable.append(feature)

        # get the noncore features
        noncore = []
        for f in ft.features:
            if f not in must1 + reasonable:
                noncore.append(f)

        noncore_index = []
        for f_i, f in enumerate(ft.features):
            if f in noncore:
                noncore_index.append(f_i)

        reasonable_child_dict = dict()
        for r in reasonable:
            child_index = [self.ft.find_fea_index(c) for c in r.children]
            reasonable_child_dict[r] = (child_index, ft.find_fea_index(r))

        # get the code func COMPLEX->SIMPLE
        # used very rare
        def novel_coding(lst):
            res = []
            for f, l in zip(ft.features, lst):
                if f not in must1+reasonable:
                    res.append(l)
            return res

        # decode func SIMPLE->COMPLEX
        # important!!
        def novel_decoding(lst):
            res = [-1] * ft.featureNum

            # copy the noncores
            for i,l in zip(noncore_index, lst):
                res[i] = l

            # adding back the must-1 s
            for i in must1_index:
                res[i] = 1

            # adding back the reasonable features
            for f in reversed(ft.features):
                if f in reasonable:
                    ll = itemgetter(*reasonable_child_dict[f][0])(res)
                    if type(ll) is int:
                        ll = [ll]

                    if f.node_type is not 'g':
                        correct = True
                        for c in f.children:
                            if c.node_type in ['m', 'g'] and res[ft.find_fea_index(c)] == 0:
                                correct = False
                                break
                        if correct:
                            res[reasonable_child_dict[f][1]] = 1
                        else:
                            res[reasonable_child_dict[f][1]] = 0

                    else:
                        res[reasonable_child_dict[f][1]] = int(f.g_u >= sum(ll) >= f.g_d)

            return res
        return noncore, novel_coding, novel_decoding

    def __init__(self, name, num_of_attached_objs=4, setConVioAsObj=True):
        self.name = name
        url = spl_addr + '/splot_data/' + self.name + '.xml'
        self.ft = load_ft_url(url)
        self.append_value_dict = dict()

        obj = [Has(name='fea', lo=0, hi=self.ft.featureNum, goal=lt)]
        if setConVioAsObj:
            obj.append(Has(name='conVio', lo=0, hi=len(self.ft.con) + 1, goal=lt))

        attach_attrs = ['cost', 'time', 'familiarity', 'app1', 'app2', 'app3'][:num_of_attached_objs]
        for a in attach_attrs:
            self.append_value_dict[a] = self._load_appendix(a)
            g = lt if append_attributes[a][2] else gt
            obj.append(Has(name=a, lo=0, hi=sum(self.append_value_dict[a]), goal=g))

        self.noncore, self.novel_coding, self.novel_decoding = self.coding_func()
        dec = [Has(l.id, 0, 1) for l in self.noncore]

        model.__init__(self, dec, obj)

    def eval(self, candidate, doNorm=True, returnFulfill=False, checkTreeStructure=False, fulfill=None):
        if not fulfill:
            fulfill = self.novel_decoding(candidate.decs)
            candidate.fulfill = fulfill
        return FeatureModel.eval(self, candidate, doNorm, returnFulfill, checkTreeStructure, fulfill)

    def genRandomCan(self, engine_version):
        raise NotImplementedError

    def genRandomTree(self):
        fulfill = [0] * self.ft.featureNum
        fulfill[0] = 1
        fulfill = self.genNode(self.ft.root, fulfill)
        decs = self.novel_coding(fulfill)
        return o(decs=decs, correct_ft=True, fulfill=fulfill)

    def ok(self, c, con_vio_tol=0):
        if not hasattr(c, 'scores'):
            self.eval(c)
        elif not c.fitness:
            self.eval(c)

        if not hasattr(c, 'correct_ft'):
            c.correct_ft = self.ft.check_fulfill_valid(c.fulfill)

        if not c.correct_ft:
            return False
        else:
            return c.conVio <= con_vio_tol

# # import debug
# ftnr = FTModelNovelRep('eshop')
# ftnr.genRandomTree()


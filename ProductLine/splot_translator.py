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
import sys
import pickle
from FeatureModel.splot_parser import load_ft_url
from universe import PROJECT_PATH

sys.dont_write_bytecode = True

"""
Translating the SPLOT feature model into dimacs format
all index starting with 1 in the dimacs format
"""


def mandatory(ft, parent, child):
    p = ft.find_fea_index(parent) + 1
    c = ft.find_fea_index(child) + 1
    c1 = '-{0} {1} 0'.format(p, c)
    c2 = '{0} -{1} 0'.format(p, c)
    return [c1, c2]


def optional(ft, parent, child):
    p = ft.find_fea_index(parent) + 1
    c = ft.find_fea_index(child) + 1
    c1 = '{0} -{1} 0'.format(p, c)
    return [c1]


def group_or(ft, parent, children):
    res = list()
    p = ft.find_fea_index(parent) + 1
    cs = [ft.find_fea_index(c)+1 for c in children]
    for i in cs:
        res.append('%d %d 0' % (-i, p))
    tmp = str(-p)
    for i in cs:
        tmp = tmp + ' ' + str(i)
    tmp += ' 0'
    res.append(tmp)
    return res


def group_exclusive_or(ft, parent, children):
    assert len(children) <= 3, "not available for group_exclusive_or for " + parent

    res = list()
    p = ft.find_fea_index(parent) + 1
    cs = [ft.find_fea_index(c) + 1 for c in children]

    for i in cs:
        res.append('%d %d 0' % (-i, p))

    tmp = str(-p)
    for i in cs:
        tmp += (' %d' % i)
    tmp += ' 0'
    res.append(tmp)

    if len(children) == 2:
        res.append('%d %d 0' % (-cs[0], -cs[1]))

    if len(children) == 3:
        res.append('%d %d %d 0' % (-cs[0], -cs[1], -cs[2]))
        res.append('%d %d %d 0' % (-cs[0], -cs[1], cs[2]))
        res.append('%d %d %d 0' % (-cs[0], cs[1], -cs[2]))
        res.append('%d %d %d 0' % (cs[0], -cs[1], -cs[2]))

    return res


def splot_translate(name):
    features = []
    ft = load_ft_url('{0}/splot_data/{1}.xml'.format(PROJECT_PATH, name))
    for f_i, fea in enumerate(ft.features):
        features.append('c {0} {1}'.format(f_i+1, fea.id))

    cnf = list()
    cnf.append('1 0')  # the root

    for fea in ft.features:
        if fea.node_type in ['m', 'g']:
            cnf.extend(mandatory(ft, fea.parent, fea))
        elif fea.node_type is 'o':
            cnf.extend(optional(ft, fea.parent, fea))

        if fea.node_type is 'g' and fea.g_u > 1:  # group_or
            cnf.extend(group_or(ft, fea, fea.children))

        if fea.node_type is 'g' and fea.g_u == 1:  # group_exclusive_or
            cnf.extend(group_exclusive_or(ft, fea, fea.children))

    for constraint in ft.con:
        tmp = ''
        for pos, lit in zip(constraint.li_pos, constraint.literals):
            if pos:
                tmp += ' ' + str(ft.find_fea_index(lit)+1)
            else:
                tmp += ' ' + str(-ft.find_fea_index(lit)-1)

        tmp += ' 0'
        tmp = tmp[1:]
        cnf.append(tmp)

    with open('{0}/dimacs_data/{1}.dimacs'.format(PROJECT_PATH, name), 'w') as f:
        for i in features:
            f.write(i)
            f.write('\n')
        f.write('p cnf %d %d\n' % (len(features), len(cnf)))
        for i in cnf:
            f.write(i)
            f.write('\n')


def load_augument(name):
    cost = []
    defects = []
    familiarity = []
    with open(PROJECT_PATH+'/input/'+name+'/cost', 'r') as f:
        cost = pickle.load(f)

    with open(PROJECT_PATH+'/input/'+name+'/defects', 'r') as f:
        defects = pickle.load(f)

    with open(PROJECT_PATH+'/input/'+name+'/familiarity', 'r') as f:
        familiarity = pickle.load(f)

    with open(PROJECT_PATH+'/dimacs_data/'+name+'.dimacs.augment', 'w') as f:
        f.write("#FEATURE_INDEX COST USED_BEFORE DEFECTS\n")
        for i, (c,u,d) in enumerate(zip(cost, familiarity, defects)):
            f.write("{0} {1} {2} {3}\n".format(i+1, c, u, d))

# splot_translate('webportal')
# splot_translate('eshop')
models = ['cellphone', 'eshop', 'webportal', 'simple']
from DimacsModel import DimacsModel
import pdb
for m in models:
    load_augument(m)
    mm = DimacsModel(m, reducedDec=True)
    with open(PROJECT_PATH+'/dimacs_data/'+m+'.dimacs.mandatory', 'w') as f:
        for i in mm.cores:
            f.write(str(i+1)+'\n')
    f = open(PROJECT_PATH+'/dimacs_data/'+m+'.dimacs.dead', 'w')
    for i in mm.deads:
        f.write(str(i+1)+'\n')
    f.close()
    f = open(PROJECT_PATH+'/dimacs_data/'+m+'.dimacs.richseed', 'w')
    f.close()

# !/usr/bin/env python
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

from ProductLine.DimacsModel import DimacsModel
from operator import itemgetter
from copy import deepcopy
import pycosat
import pdb


def pycosatSol2binstr(sol):
    """
    Demo: [1, 2, 3, -4, -5, 6, -7, -8, -9, -10] -> '1110010000'
    """
    res = ['1'] * len(sol)
    for i in sol:
        if i < 0:
            res[-i-1] = '0'
    return ''.join(res)


model = DimacsModel('ecos')
inds = []
i = 0
cnfs = deepcopy(model.cnfs)

while True:
    sat_engine = pycosat.itersolve(cnfs)
    i = 0
    for sol in sat_engine:
        i += 1
        if i > 100: break
        inds.append(model.Individual(pycosatSol2binstr(sol)))
    tmp = map(list, zip(*inds))
    tmp = map(lambda x:len(set(x)), tmp)
    group1 = [i for i,j in enumerate(tmp) if j > 1]

    print(group1)

    addition = []
    for i, j in zip(group1, itemgetter(*group1)(inds[0])):
        if j == '0':
            addition.append([-i-1])
        else:
            addition.append([i+1])

    cnfs = cnfs + addition
    inds = []

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

# from ProductLine.DimacsModel import DimacsModel
# from operator import itemgetter
# from copy import deepcopy
# import pycosat
# import pdb
#
#
# def pycosatSol2binstr(sol):
#     """
#     Demo: [1, 2, 3, -4, -5, 6, -7, -8, -9, -10] -> '1110010000'
#     """
#     res = ['.'] * len(sol)
#     for i in sol:
#         if i < 0:
#             res[-i-1] = '*'
#     return ''.join(res)
#
#
# model = DimacsModel('ecos')
# inds = []
# i = 0
# cnfs = deepcopy(model.cnfs)
#
# while True:
#     sat_engine = pycosat.itersolve(cnfs)
#     i = 0
#     for sol in sat_engine:
#         i += 1
#         # if i > 1000: break
#         print pycosatSol2binstr(sol)
#         continue
#         inds.append(model.Individual(pycosatSol2binstr(sol)))
#     tmp = map(list, zip(*inds))
#     tmp = map(lambda x:len(set(x)), tmp)
#     group1 = [i for i,j in enumerate(tmp) if j > 1]
#
#     print(group1)
#
#     addition = []
#     for i, j in zip(group1, itemgetter(*group1)(inds[0])):
#         if j == '0':
#             addition.append([-i-1])
#         else:
#             addition.append([i+1])
#
#     cnfs = cnfs + addition
#     inds = []
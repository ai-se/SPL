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

from os import sys


def write_random_individuals(ft_model, num_of_individuals=100, contain_non_leaf=False):
    cans = [ft_model.genRandomCan('v2') for _ in range(num_of_individuals)]
    map(ft_model.eval, cans)
    # write the candidates to folder surrogate_testing
    spl_addr = [i for i in sys.path if i.endswith('SPL')][0]
    with open(spl_addr+'/surrogate_data/' + ft_model.name + '.raw', 'w+') as f:
        if contain_non_leaf:
            dec_head = ['>' + i.id for i in ft_model.ft.features]
        else:
            dec_head = ['>' + i.name for i in ft_model.dec]
        obj_head = ['$' + i.name for i in ft_model.obj]
        head = ','.join(dec_head) + ',' + ','.join(obj_head)
        f.write(head)
        f.write('\n')
        for can in cans:
            if contain_non_leaf:
                f.write(','.join(map(str, can.fulfill)))
            else:
                f.write(','.join(map(str, can.decs)))
            f.write(',')
            f.write(','.join(map(str, can.fitness)))
            f.write('\n')

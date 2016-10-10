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
from os import path
import os.path
import sys
import pickle
import random

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


FT_EVAL_COUNTER = 0
PROJECT_PATH, _ = [i for i in sys.path if i.endswith('SPL')][0], \
                  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

maximize = False
minimize = True
append_attributes = {
    'familiarity': ([0, 1], maximize),
    'defects': (range(10), minimize),
    'cost': (range(5, 16), minimize),
    # 'time': (20, 1000, minimize),
    # 'app1': (0, 10, minimize),
    # 'app2': (100, 1000, minimize),
    # 'app3': (0, 1, minimize),
}


def load_appendix(model_name, feature_num, attr_name):
    subdirectories = os.listdir(PROJECT_PATH + '/input')
    if model_name not in subdirectories:
        os.mkdir(PROJECT_PATH + '/input/' + model_name)
    data_f = PROJECT_PATH + '/input/' + model_name

    try:
        with open(data_f + '/' + attr_name, 'r') as f:
            return pickle.load(f)
    except IOError:  # no such file
        values = [random.choice(append_attributes[attr_name][0]) for _ in range(feature_num)]

        # attention-- set defects=0 if familiarity = 0
        if attr_name is 'defects':
            with open(data_f + '/familiarity', 'r') as f:
                familiarities = pickle.load(f)
            for fam_i, fam in enumerate(familiarities):
                if fam == 0:
                    values[fam_i] = 0
        # END attention

        with open(data_f + '/' + attr_name, 'w') as f:
            pickle.dump(values, f)
        return values
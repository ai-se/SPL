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
import re
import os.path
import sys

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from universe import PROJECT_PATH


def load_product_url(url):
    feature_names = []
    featureNum = 0
    cnfNum = 0
    cnfs = []

    feature_name_pattern = re.compile(r'c (\d+)\$? (\w+)\n')
    stat_line_pattern = re.compile(r'p cnf (\d+) (\d+)\n')
    with open(url, 'r') as f:
        features_names_dict = dict()

        for line in f:
            if line.startswith('c'):  # record the feature names
                m = feature_name_pattern.match(line)
                """
                m.group(1) id
                m.group(2) name
                """
                features_names_dict[int(m.group(1))] = m.group(2)

            elif line.startswith('p'):
                m = stat_line_pattern.match(line)
                """
                m.group(1) feature number
                m.group(2) cnf
                """
                featureNum = int(m.group(1))
                cnfNum = int(m.group(2))

                # transfer the features_names into the list if dimacs file is valid
                assert len(features_names_dict) == featureNum, "There exists some features without any name"
                for i in range(1, featureNum+1):
                    feature_names.append(features_names_dict[i])
                del features_names_dict

            elif line.endswith('0\n'):  # the cnf
                cnfs.append(map(int, line[:-1].split(' '))[:-1])  # delete the 0, store as the lint list

            else:
                assert True, "Unknown line" + line

        assert len(cnfs) == cnfNum, "Unmatched cnfNum."

        return feature_names, featureNum, cnfs, cnfNum


def demo(name):
    url = "{0}/dimacs_data/{1}.dimacs".format(PROJECT_PATH, name)
    load_product_url(url)

if __name__ == '__main__':
    demo('uclinux')

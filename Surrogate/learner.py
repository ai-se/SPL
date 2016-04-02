from __future__ import division
import csv
import pdb
from sklearn import tree
from os import sys, path
import os
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

project_path = [i for i in sys.path if i.endswith('SPL')][0]


def _masking(L, reveals):
    """
    Example:
        L=[10,11,12,13,14]
        reveals=[2,3]
        return [12,13]
    """
    for i in range(len(L)):
        if i not in reveals:
            L[i] = 0
    return L


def get_cart(name, object_index, index_subset=[]):
    """
    get the decision tree for one objectives, whose index is given by the second parameter.
    skicit-learn tool is applied in this function.
    :param name: model name
    :param object_index:
    :return:
    """
    # load the learning material
    with open(project_path + '/surrogate_data/' + name + '.raw') as f:
        reader = csv.reader(f)
        head = reader.next()
        all_data = []
        for row in reader:
            all_data.append(row)

    # counting the decs# and objs#
    dec_num = len([i for i in head if i.startswith('>')])
    obj_num = len([i for i in head if i.startswith('$')])

    assert 0 <= object_index < obj_num, "error: check object_index again"

    # convert data from all_data
    for row in all_data:
        row[:dec_num] = map(int, row[:dec_num])
        row[dec_num:] = map(float, row[dec_num:])

    if not index_subset:
        index_subset = range(dec_num)

    x = [i for i in all_data]
    y = [i[dec_num+object_index] for i in all_data]

    map(lambda i: _masking(i, index_subset), x)  # masking

    clf = tree.DecisionTreeRegressor()
    clf = clf.fit(x, y)

    return clf


def drawTree(name, clf, obj_index=0, write_dot=True, drawPng=False, drawPdf=False):
    file2draw = "%s/surrogate_data/%s_%d" % (project_path, name, obj_index)
    if write_dot or drawPng or drawPdf:
        with open(file2draw+'.dot', 'w+') as f:
            tree.export_graphviz(clf, out_file=f)
    else:
        tree.export_graphviz(clf)
        with open('tree.dot', 'r') as f:
            tree_dot = f.read()
        os.remove('tree.dot')
        return tree_dot

    if drawPdf:
        os.system("dot -Tpdf %s.dot -o %s.pdf" % (file2draw, file2draw))
    if drawPng:
        os.system("dot -Tpng %s.dot -o %s.png" % (file2draw, file2draw))


if __name__ == '__main__':
    name = 'eshop'
    # clf = get_cart(name, 2, [2, 14, 47, 103, 112, 188, 204])
    clf = get_cart(name, 2, )
    ew = drawTree(name, clf, 2, write_dot=False)
    pdb.set_trace()

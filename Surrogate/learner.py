from __future__ import division
import csv
import pdb
from sklearn import tree
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

project_path = [i for i in sys.path if i.endswith('SPL')][0]

def get_cart(name, object_index):
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
    #pdb.set_trace()

    assert 0 <= object_index < obj_num, "error: check object_index again"

    # convert data from all_data
    for row in all_data:
        row[:dec_num] = map(int, row[:dec_num])
        row[dec_num:] = map(float, row[dec_num:])

    x = [i[:dec_num] for i in all_data]
    y = [i[dec_num+object_index] for i in all_data]

    clf = tree.DecisionTreeRegressor()
    clf = clf.fit(x, y)

    return clf


def drawTree(name, clf, obj_index = 0, drawPng=False, drawPdf=False):
    """
    temporary function
    :param name:
    :param clf:
    :return:
    """

    with open("%s/surrogate_data/%s_%d.dot" % (project_path, name, obj_index), 'w+') as f:
        tree.export_graphviz(clf, out_file=f)

    if drawPdf:
        import os
        os.system("dot -Tpdf " + project_path + '/surrogate_data/' + name + ".dot -o " +
                  project_path + '/surrogate_data/' + name + ".pdf")
    if drawPng:
        import os
        os.system("dot -Tpng " + project_path + '/surrogate_data/' + name + ".dot -o " +
                  project_path + '/surrogate_data/' + name + ".png")

if __name__ == '__main__':
    name = 'simple'
    clf = get_cart(name, 2)
    drawTree(name, clf)
    pdb.set_trace()

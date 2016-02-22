from __future__ import division
import csv
import pdb
import random
from sklearn import tree
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def mean_absolute_error(list1, list2):
    assert len(list1) == len(list2), "two arguments must have the same length"
    MAE = 0
    for i, j in zip(list1, list2):
        MAE += abs(i-j)
    MAE /= len(list1)
    return MAE


def confirm_precise(name, writeReport=False):
    # load the learning material
    spl_addr = [i for i in sys.path if i.endswith('SPL')][0]
    with open(spl_addr + '/surrogate_data/' + name + '.raw') as f:
        reader = csv.reader(f)
        head = reader.next()
        all_data = []
        for row in reader:
            all_data.append(row)
        random.shuffle(all_data)

    # prepare for the report
    if writeReport:
        report_file = open(spl_addr + '/report/' + name + '_cart_precise_test.report', 'a+')
        import time
        report_file.write('REPORT TIME: ' + time.strftime("%m-%d-%Y %H:%M") + '\n')

    # counting the decs# and objs#
    dec_num = len([i for i in head if i.startswith('>')])
    obj_num = len([i for i in head if i.startswith('$')])

    # convert data from all_data
    for row in all_data:
        row[:dec_num] = map(int, row[:dec_num])
        row[dec_num:] = map(float, row[dec_num:])

    # separate the training and test dataset
    # TODO change the testing rate
    testing_rate = 0.3
    divide_point = int(len(all_data) * testing_rate)
    train_data = all_data[:divide_point]
    test_data = all_data[divide_point:]

    X = [i[:dec_num] for i in train_data]
    Ys = []  # each obj is a Y
    for obj in range(dec_num, dec_num+obj_num):
        Ys.append([i[obj] for i in train_data])

    X_pi = [i[:dec_num] for i in test_data]
    Ys_pi = []  # each obj is a Y
    for obj in range(dec_num, dec_num+obj_num):
        Ys_pi.append([i[obj] for i in test_data])

    for j in range(obj_num):
        clf = tree.DecisionTreeRegressor()
        clf = clf.fit(X, Ys[j])
        predict_obj = clf.predict(X_pi).tolist()
        range_obj = max(Ys_pi[j])-min(Ys_pi[j])
        MAE = mean_absolute_error(Ys_pi[j], predict_obj) / range_obj
        report = "related error for obj " + head[dec_num+j][1:] + ':  ' + str(round(MAE*100, 2)) + '%'
        if writeReport:
            report_file.write(report)
            report_file.write('\n')

        print report

    if writeReport:
        report_file.write('*'*10)
        report_file.write('\n')
        report_file.close()

if __name__ == '__main__':
    from pre_surrogate import *
    from learner import *
    name = 'simple'
    write_random_individuals(name, 500, contain_non_leaf=True)
    clf = get_cart(name, 0)
    drawTree(name, clf, drawPdf=True)
    confirm_precise(name, writeReport=True)
    # pdb.set_trace()

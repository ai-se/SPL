from __future__ import division
import pdb
import csv
import matplotlib.pyplot as plt
from os import sys, path, listdir
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


project_path = filter(lambda x: x.endswith('SPL'), sys.path)[0]


def contains(s, lst):
    """
    determine whether s contains any element in the lst. Return TRUE as long as it contains at least one element.
    :param s:
    :param lst:
    :return:
    """
    for l in lst:
        if l in s:
            return True
    return False


def draw_valid_can_generate_rate(model):
    plt.clf()
    ea_records = []
    fmm_records = []
    surrogate_records = []

    lines = []

    # classify the files
    for f in listdir(project_path+'/Records/'):
        if 'stat' not in f:
            continue
        if model in f and contains(f, ['GA', 'NSGA3']):
            ea_records.append(f)
        if model in f and contains(f, ['m2', 'ms2']):
            fmm_records.append(f)

    for ear in ea_records:
        with open(project_path+'/Records/'+ear, 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader][1:]  # ignore the csv header
            cols = map(list, zip(*rows))
        evaluations = map(int, cols[1])
        valid_rate = map(float, cols[2])
        # hv = map(float, cols[3])
        timestamp = map(float, cols[4])
        start_time = min(timestamp)
        timestamp = map(lambda x: x-start_time, timestamp)

        num_valid_cans = map(lambda r: int(r*(evaluations[1]-evaluations[0])), valid_rate)
        time = []
        rate = []
        for n,s,e in zip(num_valid_cans[1:], timestamp[:-1], timestamp[1:]):
            time.append((s+e)/2)
            rate.append(n/(e-s)*60)
        lines.append((time, rate, ear.split('_')[0]))

    for fmm in fmm_records:
        with open(project_path + '/Records/' + fmm, 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader][1:]  # ignore the csv header
            cols = map(list, zip(*rows))

        num_valid_cans = cols[1]
        num_valid_cans = map(int, num_valid_cans)

        timestamp = map(float, cols[4])
        start_time = min(timestamp)
        timestamp = map(lambda x: x - start_time, timestamp)

        time = []
        rate = []
        for n, s, e in zip(num_valid_cans[1:], timestamp[:-1], timestamp[1:]):
            time.append((s + e) / 2)
            rate.append(n / (e - s) * 60)
        lines.append((time, rate, fmm.split('_')[0]))

    # plt.axis((0, 300, 0, 1000))
    for l in lines:
        plt.plot(l[0], l[1], label=l[2])
    plt.title(model + ":Candidate gen speed (#valid candidates/min)")
    plt.legend()
    plt.savefig(project_path+'/report/'+model+'_can_gen_speed')
    # plt.show()


def draw_hv_evolve(model):
    plt.clf()
    ea_records = []
    fmm_records = []
    surrogate_records = []

    lines = []

    # classify the files
    for f in listdir(project_path + '/Records/'):
        if 'stat' not in f:
            continue
        if model in f and contains(f, ['GA', 'NSGA3']):
            ea_records.append(f)
        if model in f and contains(f, ['m2', 'ms2']):
            fmm_records.append(f)

    for ear in ea_records:
        with open(project_path + '/Records/' + ear, 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader][1:]  # ignore the csv header
            cols = map(list, zip(*rows))
        hv = map(float, cols[3])
        timestamp = map(float, cols[4])
        start_time = min(timestamp)
        timestamp = map(lambda x: x - start_time, timestamp)

        time = []
        hv_evlove = []
        for h, s, e in zip(hv[1:], timestamp[:-1], timestamp[1:]):
            time.append((s + e) / 2)
            hv_evlove.append(h)
        lines.append((time, hv_evlove, ear.split('_')[0]))

    for fmm in fmm_records:
        with open(project_path + '/Records/' + fmm, 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader][1:]  # ignore the csv header
            cols = map(list, zip(*rows))

        hv = map(float, cols[3])
        timestamp = map(float, cols[4])
        start_time = min(timestamp)
        timestamp = map(lambda x: x - start_time, timestamp)

        time = []
        hv_evlove = []
        for h, s, e in zip(hv[1:], timestamp[:-1], timestamp[1:]):
            time.append((s + e) / 2)
            hv_evlove.append(h)
        lines.append((time, hv_evlove, fmm.split('_')[0]))

    # plt.axis((0, 300, 0, 1000))
    for l in lines:
        plt.plot(l[0], l[1], label=l[2])
    plt.title(model + ":Hypervolume evolve")
    plt.legend()
    plt.savefig(project_path + '/report/' + model + '_can_hv_evolve')
    # plt.show()

for model in ['eshop']:
    draw_valid_can_generate_rate(model)
    draw_hv_evolve(model)

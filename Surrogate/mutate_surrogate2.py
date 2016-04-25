from __future__ import division

import itertools
import logging
import pdb
import random
import time
import traceback
from operator import itemgetter
from os import sys

import scipy

import learner
from FeatureModel.discoverer import Discoverer
from FeatureModel.ftmodel import FTModel
from model import candidate
from tools import pareto

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "2.0"
__email__ = "jchen37@ncsu.edu"


class ConstraintConflict(Exception):
    def __init__(self, node=None, cant_set=0):
        self.node = node
        self.cant_set = cant_set

    def __str__(self):
        return repr(self.node)


class MutateSurrogateEngine2(Discoverer):
    def __init__(self, feature_model):
        time_init = time.time()
        # load the model
        self.ft_model = feature_model
        self.ft_tree = self.ft_model.ft
        self.name = self.ft_model.name
        self.var_rank_dict = dict()
        self.overflow_indicator = dict()
        logging.info("model %s load successfully." % self.name)

        '''We are using V2 engine here!! (guarantee valid)'''
        # TODO Turn off here when testing
        # pre_surrogate.write_random_individuals(self.name, 100, contain_non_leaf=True)

        logging.info("carts preparation for model %s load successfully.\nTIME CONSUMING: %d\n" %
                     (self.name, time.time() - time_init))

    def _can_set(self, after_set_filled_list):
        # checking basing on the feature constraints
        for constraint in self.ft_tree.con:
            if constraint.is_violated(self.ft_tree, after_set_filled_list):
                return False
        return True

    @staticmethod
    def _stratify_list(lst):
        """
        stratify a list.
        :param lst: Each element in the list should be a list containing N-dimension values
        :return: layers
        """
        layers = []
        not_used = map(tuple, lst)
        not_used = list(set(not_used))
        not_used = map(list, not_used)  # init as the lst, removing the unique ones

        while not_used:
            curr_layer = pareto.eps_sort(not_used)
            for c in curr_layer:
                not_used.remove(c)
            layers.append(curr_layer)
        return layers

    def best_attr_setting(self, curious_indices, g_d=0, g_u=0, rebuild=False):

        """
        what is the best settings for a flexible clusters? Answer this using the CART learner
        :param curious_indices: indices of the flexible cluster
        :param g_d: for groups only
        :param g_u: for groups only
        :param rebuild: build the learner again?
        :return: a generator
        """
        sn = hash(tuple(curious_indices))

        def _get_clf4_one_obj(obj_index):
            return learner.get_cart(self.name, obj_index, curious_indices)

        def _dec2bin_list(decimal, total_bits):
            return map(int, '{0:b}'.format(decimal).zfill(total_bits))

        if rebuild:
            self.var_rank_dict.pop(sn, None)
            self.overflow_indicator.pop(sn, None)

        if sn not in self.var_rank_dict:
            clfs = map(_get_clf4_one_obj, range(self.ft_model.objNum))
            self.var_rank_dict[sn] = []
            self.overflow_indicator[sn] = 0

            # how to rank this? -- using pareto first. then using the second layer...
            n = len(curious_indices)
            all_possibilities = []
            if g_d == 0 and g_u == 0:  # not group clusters
                if 2 ** n > 1000:
                    for _ in range(1000):
                        instance = [0] * self.ft_tree.featureNum
                        selected = random.sample(curious_indices, random.randint(1,n))
                        for s in selected:
                            instance[s] = 1
                        all_possibilities.append(instance)
                else:
                    for decimal in range(2 ** n):  # enumerate all possibilities
                        instance = [0] * self.ft_tree.featureNum
                        trying = _dec2bin_list(decimal, n)
                        for ts, t in zip(trying, curious_indices):
                            instance[t] = ts
                        all_possibilities.append(instance)
            else:
                # flexible group
                mid = int((g_d+g_u)/2)
                if scipy.misc.comb(n, mid) < 1000:
                    bit_indicator = range(n)
                    for select_bit_len in range(g_d, g_u+1):
                        for select_bit in itertools.combinations(bit_indicator, select_bit_len):
                            instance = [0] * self.ft_tree.featureNum
                            for bit in select_bit:
                                instance[curious_indices[bit]] = 1
                            all_possibilities.append(instance)
                else:
                    for _ in range(1000):
                        instance = [0] * self.ft_tree.featureNum
                        locs = random.sample(curious_indices, random.randint(g_d, g_u))
                        for loc in locs:
                            instance[loc] = 1
                        all_possibilities.append(instance)

            predict_os = []
            for clf in clfs:
                predict_os.append(map(lambda x: round(x, 1), clf.predict(all_possibilities).tolist()))  # FORCE TRUNK

            predict_os = map(list, zip(*predict_os))
            layers = self._stratify_list(predict_os)

            for layer in layers:
                layer_settings = []
                for setting, obj in zip(all_possibilities, predict_os):
                    if obj in layer:
                        layer_settings.append(itemgetter(*curious_indices)(setting))
                self.var_rank_dict[sn].append(layer_settings)

        if sn in self.var_rank_dict:
            settings_tower = self.var_rank_dict[sn]
            layer_lens = [len(l) for l in settings_tower]

            # TODO modify the sample strategy
            # each element at first layer valued 1, second layer valued 1/2, third layer valued 1/4...

            break_points = [0]
            for i, l in enumerate(layer_lens):
                break_points.append(l*0.5**i+break_points[-1])

            while True:
                if self.overflow_indicator[sn] > sum(layer_lens):
                    self.overflow_indicator[sn] = 0
                    raise ConstraintConflict

                die = random.uniform(0, break_points[-1])
                sl = break_points.index(filter(lambda b: b >= die, break_points)[0])-1  # selected_layer
                out = settings_tower[sl][random.randint(1, layer_lens[sl])-1]
                if type(out) is int:
                    yield [out]
                else:
                    yield list(out)

                self.overflow_indicator[sn] += 1

        """
            # comment till the end for an experiment
            non_dominated = pareto.eps_sort(predict_os)
            shuffle(non_dominated)

            self.var_rank_dict[sn]['all_os'] = predict_os
            self.var_rank_dict[sn]['all_os_copy'] = copy.deepcopy(predict_os)
            self.var_rank_dict[sn]['nd'] = non_dominated
            self.var_rank_dict[sn]['used'] = []

        if sn in self.var_rank_dict:
            while True:
                nd = self.var_rank_dict[sn]['nd']
                all_os = self.var_rank_dict[sn]['all_os']
                if nd[0] not in all_os:
                    del nd[0]
                if not nd:
                    assert self.var_rank_dict[sn]['all_os'], "ERROR: no more candidates available :("
                    self.var_rank_dict[sn]['nd'] = pareto.eps_sort(self.var_rank_dict[sn]['all_os'])
                    nd = self.var_rank_dict[sn]['nd']
                indices = [i for i,x in enumerate(self.var_rank_dict[sn]['all_os_copy']) if x == nd[0]]
                for index in indices:
                    all_os.remove(nd[0])
                    yield _dec2bin_list(index, len(curious_indices))
        """

    def bfs(self, filled_list):
        visited, queue = [], [self.ft_tree.root]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                try:
                    filled_list, children = self.mutate_node(vertex, filled_list)
                    visited.append(vertex)
                    queue.extend(children)

                except ConstraintConflict as cc:
                    if cc.node.node_type is 'g':
                        mutate_again_node = cc.node.parent.parent
                    else:
                        mutate_again_node = cc.node.parent
                    # TODO debug here~~~
                    try:
                        index1 = visited.index(mutate_again_node)
                        index2 = visited.index(mutate_again_node.children[0])

                        queue = visited[index1:index2]
                        visited = visited[:index1]
                    except (AttributeError, ValueError):
                        visited = []
                        queue = [self.ft_tree.root]
                        filled_list = [-1] * self.ft_tree.featureNum
                        filled_list[0] = 1  # let root be 1
        return filled_list

    def mutate_node(self, node, filled_list, trap_dict=dict()):
        node_loc = self.ft_tree.find_fea_index(node)
        node_type = node.node_type
        node_value = filled_list[node_loc]

        if node_value == 0:
            # pdb.set_trace()
            self.ft_tree.fill_subtree_0(node, filled_list)
            if not self._can_set(filled_list):
                raise ConstraintConflict(node, cant_set=0)
            return filled_list, []

        '''otherwise, current node is required, then assign the value of its children'''
        m_child = [c for c in node.children if c.node_type in ['r', 'm', 'g']]
        g_child = [c for c in node.children if c.node_type == '']
        o_child = [c for c in node.children if c.node_type == 'o']
        filled_list_copy = [fl for fl in filled_list]  # make a duplicate

        '''
        children setting sorting
        using decision tree technique. Train data from the valid candidates
        '''
        if node_type is 'g':
            g_u, g_d = node.g_u, node.g_d
        else:
            g_u = g_d = 0

        if o_child or g_child:
            curious_indices = map(self.ft_tree.find_fea_index, o_child+g_child)
            best_gen = self.best_attr_setting(curious_indices, g_d, g_u)

        while True:
            filled_list = [flc for flc in filled_list_copy]  # recover

            for m in m_child:
                m_i = self.ft_tree.find_fea_index(m)
                filled_list[m_i] = 1

            # we have flexible choices here
            if o_child or g_child:
                # TODO support for both o_child and g_child...
                try:
                    bit_setting = best_gen.next()
                except ConstraintConflict:
                    raise ConstraintConflict(node, cant_set=1)

                for index, bit in zip(curious_indices, bit_setting):
                    filled_list[index] = bit

            if self._can_set(filled_list):
                return filled_list, m_child + g_child + o_child
            elif len(o_child) + len(g_child) == 0:
                raise ConstraintConflict(node, cant_set=1)

    def _fetch_leaves(self, fulfill):
        r = []
        for x in self.ft_tree.leaves:
            index = self.ft_tree.features.index(x)
            r.append(fulfill[index])
        return r

    def gen_valid_one(self):
        filled_list = [-1] * self.ft_tree.featureNum
        filled_list[0] = 1  # let root be 1
        filled_list = self.bfs(filled_list)
        leaves = self._fetch_leaves(filled_list)

        can = candidate(decs=leaves)
        can.fulfill = filled_list
        return can

def run():

def test_one_model(model):
    R = []
    engine = MutateSurrogateEngine2(FTModel(model, setConVioAsObj=False))
    for i in range(100):
        print i
        alpha = engine.gen_valid_one()
        engine.ft_model.eval(alpha)
        R.append(alpha)
    pdb.set_trace()

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = [
            # 'simple',
            # 'webportal',
            # 'cellphone',
            # 'eshop',
            'eis',
        ]
        for model in to_test_models:
            test_one_model(model)
    except Exception:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

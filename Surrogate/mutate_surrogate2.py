from __future__ import division
from __init__ import *
from random import choice, randint, shuffle
from operator import itemgetter
from os import sys
from FeatureModel.discoverer import Discoverer
from FeatureModel.ftmodel import FTModel
import copy
import pre_surrogate
import learner
import pareto
import logging
import pdb
import traceback
import time
import UNIVERSE


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.4"
__email__ = "jchen37@ncsu.edu"


class BadPathConflict(Exception):
    def __init__(self, node, cant_set):
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
        logging.info("model %s load successfully." % self.name)

        # get one decision tree for each objective and prune them.
        # We are using V2 engine here!! (guarantee valid)
        pre_surrogate.write_random_individuals(self.name, 100, contain_non_leaf=True)  # TODO Turn off here when testing
        # for obj_index, _ in enumerate(self.ft_model.obj):
        #     clf = learner.get_cart(name, obj_index)
        #     learner.drawTree(name, clf, obj_index)

        # self.carts = [CART(name, obj_index) for obj_index, _ in enumerate(self.ft_model.obj)]
        # map(lambda cart: cart.prune(remaining_rate=0.3), self.carts)
        logging.info("carts preparation for model %s load successfully.\nTIME CONSUMING: %d\n" %
                     (self.name, time.time() - time_init))

        # self.avoid_paths = self._get_avoid_paths()
        # pdb.set_trace()

    def _get_avoid_paths(self):
        result_set = []
        for cart in self.carts:
            avoid_paths = cart.translate_into_binary_list(cart.get_bad_paths(), len(self.ft_tree.features))
            result_set.extend(avoid_paths)

        # remove the duplicate
        import itertools
        result_set.sort()
        return list(result_set for result_set, _ in itertools.groupby(result_set))

    def _can_set(self, after_set_filled_list):
        # checking basing on the avoiding paths
        for avoid_path in self.avoid_paths:
            checking = [index for index, path_point in enumerate(avoid_path) if path_point != -1]
            if itemgetter(*checking)(avoid_path) == itemgetter(*checking)(after_set_filled_list):
                return False
        return True

    # @contextmanager
    def best_attr_setting(self, curious_indices, rebuild=False):
        sn = hash(tuple(curious_indices))

        def _get_clf4_one_obj(obj_index):
            return learner.get_cart(self.name, obj_index, curious_indices)

        def _dec2bin_list(decimal, total_bits):
            return map(int, '{0:b}'.format(decimal).zfill(total_bits))

        if rebuild:
            self.var_rank_dict.pop(sn, None)

        if sn not in self.var_rank_dict:
            clfs = map(_get_clf4_one_obj, range(self.ft_model.objNum))
            self.var_rank_dict[sn] = dict()

            # TODO how to rank this? -- using pareto first. then using the second layer...
            n = len(curious_indices)
            all_possibilities = []
            for decimal in range(2**n):  # enumerate all possibilities
                instance = [0] * self.ft_tree.featureNum
                trying = _dec2bin_list(decimal, n)
                for ts, t in zip(trying, curious_indices):
                    instance[t] = ts
                all_possibilities.append(instance)

            predict_os = []
            for clf in clfs:
                predict_os.append(map(lambda x: round(x, 1), clf.predict(all_possibilities).tolist()))  # FORCE TRUNK

            predict_os = map(list, zip(*predict_os))
            non_dominated = pareto.eps_sort(predict_os)
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

    def bfs(self, filled_list):
        visited, queue = set(), [self.ft_tree.root]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                try:
                    filled_list, childs = self.mutate_node(vertex, filled_list)
                except BadPathConflict as bb:
                    pdb.set_trace()
                queue.extend(childs)
        return filled_list

    def mutate_node(self, node, filled_list):
        node_loc = self.ft_tree.find_fea_index(node)
        node_type = node.node_type
        node_value = filled_list[node_loc]

        if node_value == 0:
            pass
            # TODO
            return
            # # pdb.set_trace()
            # self.ft_tree.fill_subtree_0(node, filled_list)
            # if not self._can_set(filled_list):
            #     raise BadPathConflict(node, cant_set=node_value)
            # return filled_list, []

        '''otherwise, current node is required, then assign the value of its children'''
        m_child = [c for c in node.children if c.node_type in ['r', 'm', 'g']]
        g_child = [c for c in node.children if c.node_type == '']
        o_child = [c for c in node.children if c.node_type == 'o']
        filled_list_copy = [fl for fl in filled_list]  # make a duplicate

        '''
        children setting sorting
        using decision tree technique. Tranining data from the valid candidates
        '''
        if node_type is 'g':
            g_c = node.g_u - node.g_d
        else:
            g_c = 0

        if o_child or g_c:
            # the children assignment is flexible
            curious_indices = map(self.ft_tree.find_fea_index, g_child + o_child)
            # with self.best_attr_setting(curious_indices) as best_var:
            #     for i in best_var:
            #         print i
            gen = self.best_attr_setting(curious_indices)
            while 1:
                print gen.next()

            # self.best_attr_setting(curious_indices).next()
            pdb.set_trace()
            pass



        # TODO all possible ?
        while True:
            filled_list = [flc for flc in filled_list_copy]  # recover
            for m in m_child:
                m_i = self.ft_tree.find_fea_index(m)
                filled_list[m_i] = 1
            for o in o_child:
                # TODO for next version: the orders matter
                o_i = self.ft_tree.find_fea_index(o)
                filled_list[o_i] = choice([0, 1])

            alpha = []
            if node_type is 'g':
                r = randint(node.g_d, node.g_u)
                alpha = [1] * r + [0] * (len(g_child) - r)
                shuffle(alpha)

            for assign, g in zip(alpha, g_child):
                g_i = self.ft_tree.find_fea_index(g)
                filled_list[g_i] = assign

            if self._can_set(filled_list):
                return filled_list, m_child + g_child + o_child

            tol -= 1
            if not tol:
                raise BadPathConflict(node, cant_set=node_value)

    def gen_valid_one(self):
        filled_list = [-1] * self.ft_tree.featureNum
        filled_list[0] = 1  # let root be 1
        self.bfs(filled_list)
        # self.mutate_node(self.ft_tree.root, filled_list)
        return filled_list
        # pdb.set_trace()


def test_one_model(model):
    UNIVERSE.FT_EVAL_COUNTER = 0
    engine = MutateSurrogateEngine2(FTModel(model, setConVioAsObj=False))
    alpha = engine.gen_valid_one()
    # pdb.set_trace()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = [
            # 'simple',
            'webportal',
            # 'cellphone',
            # 'eshop',
            # 'eis',
        ]
        for model in to_test_models:
            test_one_model(model)
            # pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

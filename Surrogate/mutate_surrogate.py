from __future__ import division
from cart import CART
from random import choice, randint, shuffle
from operator import itemgetter
from copy import deepcopy
from os import sys
from FeatureModel.discoverer import Discoverer
from FeatureModel.ftmodel import FTModel
import pre_surrogate
import learner
import logging
import pdb
import traceback
import time
import UNIVERSE

project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.2"
__email__ = "jchen37@ncsu.edu"

# engine abandoned. Apr 4, 2016


class BadPathConflict(Exception):
    def __init__(self, node, cant_set):
        self.node = node
        self.cant_set = cant_set

    def __str__(self):
        return repr(self.node)


class MutateWithSurrogateEngine(Discoverer):
    def __init__(self, feature_model):
        time_init = time.time()
        # load the model
        self.ft_model = feature_model
        self.ft_tree = self.ft_model.ft
        name = self.ft_model.name
        logging.info("model %s load successfully." % name)

        # get one decision tree for each objective and prune them.
        pre_surrogate.write_random_individuals(name, 100, contain_non_leaf=True)  # TODO Turn off here when testing
        for obj_index, _ in enumerate(self.ft_model.obj):
            clf = learner.get_cart(name, obj_index)
            learner.drawTree(name, clf, obj_index)
        """
        beginning testing
        """
        pdb.set_trace()
        """
        end of testing
        """
        exit(0)

        self.carts = [CART(name, obj_index) for obj_index, _ in enumerate(self.ft_model.obj)]
        map(lambda cart: cart.prune(remaining_rate=0.3), self.carts)
        logging.info("carts for model %s load successfully.\nTIME CONSUMING: %d\n" % (name, time.time()-time_init))

        self.avoid_paths = self._get_avoid_paths()
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
        node_loc = self.ft_tree.features.index(node)
        node_type = node.node_type
        node_value = filled_list[node_loc]

        if node_value == 0:
            # pdb.set_trace()
            self.ft_tree.fill_subtree_0(node, filled_list)
            if not self._can_set(filled_list):
                raise BadPathConflict(node, cant_set=node_value)
            return filled_list, []

        '''otherwise, current node is required, then assign the value of its children'''
        m_child = [c for c in node.children if c.node_type in ['r', 'm', 'g']]
        g_child = [c for c in node.children if c.node_type == '']
        o_child = [c for c in node.children if c.node_type == 'o']
        filled_list_copy = deepcopy(filled_list)

        tol = 20  # TODO how to set this?
        while True:
            filled_list = deepcopy(filled_list_copy)
            for m in m_child:
                m_i = self.ft_tree.features.index(m)
                filled_list[m_i] = 1
            for o in o_child:
                # TODO for next version: the orders matter
                o_i = self.ft_tree.features.index(o)
                filled_list[o_i] = choice([0, 1])

            alpha = []
            if node_type == 'g':
                r = randint(node.g_d, node.g_u)
                alpha = [1] * r + [0] * (len(g_child)-r)
                shuffle(alpha)

            for assign, g in zip(alpha, g_child):
                g_i = self.ft_tree.features.index(g)
                filled_list[g_i] = assign

            if self._can_set(filled_list):
                return filled_list, m_child+g_child+o_child

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

    # def for_testing_bad_paths(self):
    #     all_p = [
    #         [1, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    #         [1, 1, 1, 0, 1, 0, 1, 1, 1, 0],
    #         [1, 1, 1, 0, 0, 1, 1, 1, 1, 0],
    #
    #         [1, 1, 1, 1, 0, 0, 1, 1, 0, 1],
    #         [1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    #         [1, 1, 1, 0, 0, 1, 1, 1, 0, 1],
    #
    #         [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    #         [1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
    #         [1, 1, 1, 0, 0, 1, 0, 0, 0, 0],
    #
    #     ]
    #
    #     for i in all_p:
    #         print self._can_set(i)


def test_one_model(model):
    UNIVERSE.FT_EVAL_COUNTER = 0
    engine = MutateWithSurrogateEngine(FTModel(model))
    # pdb.set_trace()
    # alpha = engine.gen_valid_one()
    # pdb.set_trace()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = [
            # 'simple',
            # 'webportal',
            # 'cellphone',
            'eshop',
            # 'eis',
        ]
        for model in to_test_models:
            test_one_model(model)
            # pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


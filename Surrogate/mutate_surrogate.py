from __future__ import division
import pre_surrogate
import learner
from cart import *
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from FeatureModel.ftmodel import FTModel
from FeatureModel.parser import *
from FeatureModel.discoverer import Discoverer
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class MutateWithSurrogateEngine(Discoverer):
    def __init__(self, feature_model):
        # load the model
        self.ft_model = feature_model
        self.ft_tree = self.ft_model.ft
        name = self.ft_model.name
        logging.info("model %s load successfully." % name)

        # get one decision tree for each objective and prune them
        for obj_index, _ in enumerate(self.ft_model.obj):
            pre_surrogate.write_random_individuals(name, 500, contain_non_leaf=True)
            clf = learner.get_cart(name, obj_index)
            learner.drawTree(name, clf, obj_index)

        self.carts = [CART(name, obj_index) for obj_index, _ in enumerate(self.ft_model.obj)]
        map(lambda cart: cart.prune(remaining_rate=0.3), self.carts)
        logging.info("carts for model %s load successfully." % name)

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
            for i, j in zip(avoid_path, after_set_filled_list):
                if i == 0 and j == 1:
                    return False
                if i == 1 and j == 0:
                    return False
        return True

    def mutateNode(self, node, filled_list):
        node_loc = self.ft_tree.features.index(node)
        node_type = node.node_type
        node_value = filled_list[node_loc]

        if node_type in ['r', 'm']:
            1
            # setting children of a mandatory node
            # TODO
        elif node_type == 'g':
            1
            # TODO children of a group node
        elif node_type == 'o':
            1
            # TODO children of optional node
        else:  # leaves
            1
            # TODO we have arrived a leaf
        pdb.set_trace()
        pass

    def gen_valid_one(self):
        filled_list = [-1] * self.ft_tree.featureNum
        filled_list[0] = 1  # let root be 1
        self.mutateNode(self.ft_tree.root, filled_list)

        pdb.set_trace()
        # TODO ...


def test_one_model(model):
    engine = MutateWithSurrogateEngine(model)
    print 'Decision num: %d' % engine.ft_model.decNum
    print 'Bad paths num: %d' % len(engine.avoid_paths)
    print '*' * 8
    engine.genValidOne()


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = ['simple', 'webportal', 'cellphone', 'eshop', 'eis']
        for model in to_test_models:
            test_one_model(model)
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


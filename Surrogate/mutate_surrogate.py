from __future__ import division
import pre_surrogate
import learner
from cart import *
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from Parser.ftmodel import FTModel
from Parser.parser import *
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class MutateWithSurrogateEngine(object):
    def __init__(self, name):
        # load the model
        self.ft_model = FTModel(name)
        self.ft_tree = self.ft_model.ft
        logging.info("model %s load successfully." % name)

        # get one decision tree for each objective and prune them
        for obj_index in range(len(self.ft_model.obj)):
            pre_surrogate.write_random_individuals(name, 500, contain_non_leaf=True)
            clf = learner.get_cart(name, obj_index)
            learner.drawTree(name, clf, obj_index)

        self.carts = [CART(name, obj_index) for obj_index in range(len(self.ft_model.obj))]
        for cart in self.carts:
            cart.prune(remaining_rate=0.3)
        logging.info("carts for model %s load successfully." % name)

        self.avoid_paths = self._get_avoid_paths()

    def _get_avoid_paths(self):
        result_set = []
        for cart in self.carts:
            avoid_paths = cart.translate_into_binary_list(cart.get_bad_paths(), len(self.ft_tree.features))
            result_set.extend(avoid_paths)

        # remove the duplicate
        import itertools
        result_set.sort()
        return list(result_set for result_set,_ in itertools.groupby(result_set))

    def genValidOne(self, returnFulfill=True):
        # TODO core function
        return self, returnFulfill

if __name__ == '__main__':
    import time
    try:
        logging.basicConfig(level=logging.CRITICAL, format='Line %(lineno)d at %(filename)s:\t %(message)s')
        to_test_models = ['simple', 'webportal', 'cellphone', 'eshop', 'eis']
        for model in to_test_models:
            start_time = time.time()
            engine = MutateWithSurrogateEngine(model)
            end_time = time.time()
            pdb.set_trace()
            print model
            print 'init time: %d'% (end_time - start_time)
            print 'Decision num: %d' % engine.ft_model.decNum
            print 'Bad paths num: %d' % len(engine.avoid_paths)
            print '*' * 8
        pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


from __future__ import division
import pdb
import re
import traceback
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class CART(object):
    class CartNode(object):
        def __init__(self, info_dict, parent_index=-1, true_hand_child=None, false_hand_child=None):
            self._info_dict = info_dict

            # safe checking
            assert 'is_leaf' in self._info_dict.keys(), "claim whether this is a leaf"
            if not self._info_dict['is_leaf']:
                assert 'X' in self._info_dict.keys(), "set up cart node determined X"
                assert 'op' in self._info_dict.keys(), "set up the operator"
                assert 'op_right' in self._info_dict.keys(), "set up op right"
            assert 'mse' in self._info_dict.keys(), "set up cart node mse"
            assert 'samples' in self._info_dict.keys(), "set up number of samples"
            assert 'value' in self._info_dict.keys(), "set up the value"

            self.is_leaf = self._info_dict['is_leaf']
            self.value = self._info_dict['value']
            self.mse = self._info_dict['mse']
            self.samples = self._info_dict['samples']
            self.parent_index = parent_index  # note: set parent of root -1
            if not self.is_leaf:
                self.true_child = true_hand_child
                self.false_child = false_hand_child

        def testing(self, x_list):
            """
            given the list of X, determine go to True, or go to false
            :param x_list:
            :return: boolean result
            """
            fetch = x_list[self._info_dict['X']]
            right = self._info_dict['op_right']
            op = self._info_dict['op']
            if op == '<':
                return fetch < right
            if op == '<=':
                return fetch <= right
            if op in ['=', '==']:
                return fetch == right
            if op == '>':
                return fetch > right
            if op == '>=':
                return fetch >= right

    def __init__(self, name_of_model):
        self.model_name = name_of_model
        self.root = None
        self.nodes = []
        self._load_dot_file()

    def _load_dot_file(self):
        # read the dot file
        records = []
        with open(project_path + '/surrogate_data/' + self.model_name + '.dot', 'r') as f:
            for record in f:
                records.append(record[:-1])  # ignore the final \n

        # parsing by regular expression engine
        connection_pattern = re.compile(r'(\d+) -> (\d+) .*;')
        non_leaf_node_pattern = re.compile(r'(\d+) '  # group 1 node index
                                           r'\[label=\"X\[(\d+)\]'  # group 2 X?
                                           r' ([<>=]+) '  # group 3 operator
                                           r'([-]?\d+\.\d+)'  # group 4 right of operator
                                           r'\\nmse = '
                                           r'([-]?\d+\.\d+)'  # group 5 mse
                                           r'\\nsamples = '
                                           r'(\d+)'  # group 6 samples
                                           r'\\nvalue = '
                                           r'([-]?\d+\.\d+)'  # group 7 value
                                           r'.*')

        leaf_node_pattern = re.compile(r'(\d+) '  # group 1 node index
                                       r'\[label=\"mse = '
                                       r'([-]?\d+\.\d+)'  # group 2 mse
                                       r'\\nsamples = '
                                       r'(\d+)'  # group 3 samples
                                       r'\\nvalue = '
                                       r'([-]?\d+\.\d+)'  # group 4 value
                                       r'.*')

        for record in records:
            if len(record) <= 1 or (not record[0].isdigit()):  # useless info
                continue

            grouped_record_info = connection_pattern.match(record)
            if grouped_record_info:  # connection found
                start = int(grouped_record_info.group(1))
                end = int(grouped_record_info.group(2))
                self.nodes[end].parent_index = start
                if not self.nodes[start].true_child:
                    self.nodes[start].true_child = self.nodes[end]
                else:
                    self.nodes[start].false_child = self.nodes[end]
                continue

            grouped_record_info = non_leaf_node_pattern.match(record)
            if grouped_record_info:  # non-leaf node found
                temp_info_dict = {
                    'is_leaf': False,
                    'X': int(grouped_record_info.group(2)),
                    'op': grouped_record_info.group(3),
                    'op_right': float(grouped_record_info.group(4)),
                    'mse': float(grouped_record_info.group(5)),
                    'samples': int(grouped_record_info.group(6)),
                    'value': float(grouped_record_info.group(7))
                }
                self.nodes.append(self.CartNode(temp_info_dict))
                assert len(self.nodes)-1 == int(grouped_record_info.group(1)), "cannot use append?"
                continue

            grouped_record_info = leaf_node_pattern.match(record)
            if grouped_record_info:  # leaf node found
                temp_info_dict = {
                    'is_leaf': True,
                    'mse': float(grouped_record_info.group(2)),
                    'samples': int(grouped_record_info.group(3)),
                    'value': float(grouped_record_info.group(4))
                }
                self.nodes.append(self.CartNode(temp_info_dict))
                assert len(self.nodes)-1 == int(grouped_record_info.group(1)), "cannot use append?"
                continue

            assert False, "errors in matching" + record

        self.root = self.nodes[0]

    def prune(self, remaining_rate=0.3, less_is_more=True):
        """
        prune the decision tree. Prune start from the leaves. Remove one node if its leaf&right child have both been
        removed. (this process will do recursively)
        :param remaining_rate:
        :param less_is_more:
        :return:
        """
        leaf_values = [node.value for node in ca.nodes if node.is_leaf]
        cutting_cursor = min(max(int(len(leaf_values)*remaining_rate), 0), len(leaf_values)-1)
        cut = sorted(leaf_values, reverse=not less_is_more)[cutting_cursor]
        for node in self.nodes:
            if node.is_leaf:
                if (node.value <= cut and less_is_more) or (node.value >= cut and not less_is_more):
                    continue
                # TODO delete the node and remove the pointer at parent node




def test():
    cart = CART('webportal')
    # cart.prune()
    pdb.set_trace()

if __name__ == '__main__':
    try:
        test()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

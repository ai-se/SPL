from __future__ import division
import pdb
import re
import traceback
import logging
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.2"
__email__ = "jchen37@ncsu.edu"


class CART(object):
    class CartNode(object):
        def __init__(self, info_dict, parent=None, true_hand_child=None, false_hand_child=None):
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
            self.parent = parent  # note: set parent of root None
            if not self.is_leaf:
                self.x = int(self._info_dict['X'])
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

    def __init__(self, name_of_model, obj_index=0):
        self.model_name = name_of_model
        self.root = None
        self.nodes = []
        self._load_dot_file(obj_index)

    def _load_dot_file(self, obj_index):
        # read the dot file
        records = []
        with open("%s/surrogate_data/%s_%d.dot" % (project_path, self.model_name, obj_index), 'r') as f:
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
                self.nodes[end].parent = self.nodes[start]
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
        leaf_values = [node.value for node in self.nodes if node.is_leaf]
        cutting_cursor = min(max(int(len(leaf_values)*remaining_rate), 0), len(leaf_values)-1)
        cut = sorted(leaf_values, reverse=not less_is_more)[cutting_cursor]

        logging.debug("Pruning the CART...")
        logging.debug("before prune, node #: "+str(len(self.nodes)))

        to_remove_nodes = []
        for node in self.nodes:
            if node.is_leaf:
                if (node.value <= cut and less_is_more) or (node.value >= cut and not less_is_more):
                    continue

                if node.parent.true_child == node:
                    node.parent.true_child = None
                else:
                    node.parent.false_child = None
                to_remove_nodes.append(node)

        # delete the bad leaves
        for kill_node in to_remove_nodes:
            self.nodes.remove(kill_node)

        logging.debug('inter # '+str(len(self.nodes)))

        # recursively delete the bad subtree
        to_remove_nodes = ['just_to_start!']
        while to_remove_nodes:
            to_remove_nodes = []
            for node in self.nodes[1:]:
                if (hasattr(node, 'true_child') and node.true_child) or \
                        (hasattr(node, 'false_child') and node.false_child) or \
                        node.is_leaf:
                    continue

                # releasing this node
                if hasattr(node.parent, 'true_child') and node.parent.true_child == node:
                    node.parent.true_child = None
                else:
                    node.parent.false_child = None
                to_remove_nodes.append(node)

            for kill_node in to_remove_nodes:
                self.nodes.remove(kill_node)

        logging.debug("after prune, node #: " + str(len(self.nodes)))
        # pdb.set_trace()

    def get_bad_paths(self):
        """
        this function should be called after pruned.
        return the paths which have been pruned, that is the bad paths
        :return: list of bad paths. each path expressed as [True,False,False...]
        """

        def find_full_path_from_end(self, end_node, end_node_direction):
            path = [end_node_direction]
            parent = end_node.parent

            while end_node is not self.root:
                if hasattr(parent, 'true_child') and parent.true_child is end_node:
                    end_node_direction = True
                else:
                    end_node_direction = False
                path.insert(0, end_node_direction)

                end_node = parent
                parent = end_node.parent

            return path

        bad_paths = []
        for node in self.nodes:
            if (hasattr(node, 'true_child') and node.true_child and hasattr(node, 'false_child') and node.false_child) \
                    or node.is_leaf:
                continue
            direction = hasattr(node, 'true_child') and node.true_child
            bad_paths.append(find_full_path_from_end(self, node, not direction))

        return bad_paths

    def translate_into_binary_list(self, bad_paths, x_list_length):
        """
        translate the standard bad paths into binary list. -1 in the binary list indicates no information provides.
        :param bad_paths:
        :param x_list_length:
        :return:
        """

        if type(bad_paths) is not list:
            bad_paths = [bad_paths]

        binary_bad_paths = []
        for bad_path in bad_paths:
            binary_bad_path = [-1] * x_list_length
            current_node = self.root
            for direction_cursor in bad_path:
                tmp_x = current_node.x
                binary_bad_path[tmp_x] = 1
                if not (current_node.testing(binary_bad_path) == direction_cursor):
                    binary_bad_path[tmp_x] = 0

                if direction_cursor:
                    current_node = current_node.true_child
                else:
                    current_node = current_node.false_child

            binary_bad_paths.append(binary_bad_path)

        return binary_bad_paths


def test():
    cart = CART('simple')
    cart.prune()
    ww = cart.get_bad_path()
    qq = cart.translate_into_binary_list(ww, 10)
    pdb.set_trace()

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG, format='Line %(lineno)d info:  %(message)s')
        test()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


from __future__ import division
import pdb
import re
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
project_path = [i for i in sys.path if i.endswith('SPL')][0]

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class CART(object):
    class cart_node(object):
        def __init__(self, info_dict, parent_index, true_hand_child_index=-1, false_hand_child_index=-1):
            self.info_dict = info_dict
            assert self.info_dict['is_leaf'], "please claim whether this is a leaf"

            assert self.info_dict['X'], "please set up cart node determined X"
            assert self.info_dict[]

    def __init__(self, name_of_model):
        self.model_name = name_of_model

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
            grouped_record_info = connection_pattern.match(record)
            if grouped_record_info:
                continue  # TODO connection found

            grouped_record_info = non_leaf_node_pattern.match(record)
            if grouped_record_info:
                continue  # TODO non-leaf node found

            grouped_record_info = leaf_node_pattern.match(record)
            if grouped_record_info:
                continue  # TODO leaf node found


        return False

pdb.set_trace()
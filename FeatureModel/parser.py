import re
import xml.etree.ElementTree
import numpy as np
from Feature_tree import FeatureTree, Node, Constraint

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def load_ft_url(url):
    # load the feature tree and constraints
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()

    for child in root:
        if child.tag == 'feature_tree':
            feature_tree = child.text
        if child.tag == 'constraints':
            constraints = child.text

    # initialize the feature tree
    ft = FeatureTree()

    # parse the feature tree text
    feas = feature_tree.split("\n")
    feas = filter(bool, feas)
    common_feature_pattern = re.compile('(\t*):([romg]?).*\W(\w+)\W.*')
    group_pattern = re.compile('\t*:g \W(\w+)\W \W(\d),([\d\*])\W.*')
    layer_dict = dict()
    for f in feas:
        m = common_feature_pattern.match(f)
        """
        m.group(1) layer
        m.group(2) type
        m.group(3) id
        """
        layer = len(m.group(1))
        t = m.group(2)
        if t == 'r':
            tree_root = Node(identification=m.group(3), node_type='r')
            layer_dict[layer] = tree_root
            ft.set_root(tree_root)
        elif t == 'g':
            mg = group_pattern.match(f)
            """
            mg.group(1) id
            mg.group(2) down_count
            mg.group(3) up_count
            """
            gNode = Node(identification=mg.group(1), parent=layer_dict[layer - 1], node_type='g')
            layer_dict[layer] = gNode
            if mg.group(3) == '*':
                gNode.g_u = np.inf
            else:
                gNode.g_u = mg.group(3)
            gNode.g_d = mg.group(2)
            layer_dict[layer] = gNode
            gNode.parent.add_child(gNode)
        else:
            treeNode = Node(identification=m.group(3), parent=layer_dict[layer - 1], node_type=t)
            layer_dict[layer] = treeNode
            treeNode.parent.add_child(treeNode)

    # parse the constraints
    cons = constraints.split('\n')
    cons = filter(bool, cons)
    common_con_pattern = re.compile('(\w+):(~?)(\w+)(.*)\s*')
    common_more_con_pattern = re.compile('\s+(or) (~?)(\w+)(.*)\s*')

    for cc in cons:
        literal = []
        li_pos = []
        m = common_con_pattern.match(cc)
        con_id = m.group(1)
        li_pos.append(not bool(m.group(2)))
        literal.append(m.group(3))
        while m.group(4):
            cc = m.group(4)
            m = common_more_con_pattern.match(cc)
            li_pos.append(not bool(m.group(2)))
            literal.append(m.group(3))
        """
         con_id: constraint identifier
         literal: literals
         li_pos: whether is positive or each literals
        """
        con_stmt = Constraint(identification=con_id, literals=literal, literals_pos=li_pos)
        ft.add_constraint(con_stmt)

    ft.set_features_list()

    return ft

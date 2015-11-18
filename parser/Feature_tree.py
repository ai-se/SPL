import pdb
import numpy as np
import random
import pickle
import os


class Node(object):
    def __init__(self, id, parent = None, node_type = 'o'):
        self.id = id
        self.parent = parent
        self.node_type = node_type
        self.children = []
        if node_type == 'g':
            self.g_u = 1
            self.g_d = 0

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def __repr__(self):
        return '\nid: %s\ntype:%s\n'%(
            self.id,
            self.node_type)

class Constraint(object):
    def __init__(self, id, literals, literals_pos):
        self.id = id
        self.literals = literals
        self.li_pos = literals_pos

    def __repr__(self):
        return self.id+'\n'+str(self.literals)+'\n'+str(self.li_pos)

    def iscorrect(self, ft, filledForm):
        for (li, pos) in zip(self.literals, self.li_pos):
            i = ft.find_fea_index_by_id(li)
            if int(pos) == filledForm[i]: return True
        return False


class FeatureTree(object):
    def __init__(self):
        self.root = None
        self.features = []
        self.groups = []
        self.leaves = []
        self.con = []
        self.cost = []
        self.featureNum = 0

    def set_root(self,root):
        self.root = root

    def add_constraint(self,con):
        self.con.append(con)

    def find_fea_index_by_id(self, id):
        for i,x in enumerate(self.features):
            if x.id == id:
                return i

    # featch all the features in the tree basing on the children structure
    def set_features_list(self):
        def setting_feature_list(self,node):
            if node.node_type == 'g':
                node.g_u = int(node.g_u) if node.g_u != np.inf else len(node.children)
                node.g_d = int(node.g_d) if node.g_d != np.inf else len(node.children)
                self.features.append(node)
                self.groups.append(node)
            if node.node_type != 'g':
                self.features.append(node)
            if len(node.children) == 0:
                self.leaves.append(node)
            for i in node.children:
                setting_feature_list(self, i)
        setting_feature_list(self, self.root)
        self.featureNum = len(self.features)

    def postorder(self, node, func, extraArgs = []):
        if node.children:
            for c in node.children:
                self.postorder(c,func, extraArgs)
        func(node, *extraArgs)


    # setting the form by the structure of feature tree
    # leaves should be filled in the form in advanced
    # all not filled feature should be -1 in the form
    def fillForm4AlFea(self, form):
        def filling(node):
            index = self.features.index(node)
            if form[index] != -1:
                return
            # handeling the group featues
            if node.node_type == 'g':
                sum = 0
                for c in node.children:
                    i_index = self.features.index(c)
                    sum += form[i_index]
                form[index] = 1 if sum >= node.g_d and sum <= node.g_u else 0
                return

            """
            # the child is a group
            if node.children[0].node_type == 'g':
                form[index] = form[index+1]
                return
            """

            #handeling the other type of node
            m_child = [x for x in node.children if x.node_type in ['m','r','g']]
            o_child = [x for x in node.children if x.node_type == 'o']
            if len(m_child) == 0: #all children are optional
                s = 0
                for o in o_child:
                    i_index = self.features.index(o)
                    s += form[i_index]
                form[index] = 1 if s>0 else 0
                return
            for m in m_child:
                i_index = self.features.index(m)
                if form[i_index] == 0:
                    form[index] = 0
                    return
            form[index] = 1
            return

        self.postorder(self.root, filling)

    def getFeatureNum(self):
        return len(self.features) - len(self.groups)

    def getConsNum(self):
        return len(self.con)

    def _genRandomCost(self,tofile):
        any=random.random
        self.cost = [any() for _ in self.features]
        f = open(tofile, 'w')
        pickle.dump(self.cost, f)
        f.close()

    def loadCost(self, fromfile):
        if not os.path.isfile(fromfile):
            self._genRandomCost(fromfile)
        f = open(fromfile)
        self.cost = pickle.load(f)
        f.close()

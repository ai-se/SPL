import os,sys,random
galedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/GALE/'
sys.path.insert(0,galedir)

import pdb,re
import xml.etree.ElementTree as ET
import numpy as np
from Feature_tree import *
from model import *

def load_ft_url(url):
    # load the feature tree and constraints
    tree = ET.parse(url)
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
            treeRoot = Node(id = m.group(3), node_type = 'r')
            layer_dict[layer] = treeRoot
            ft.set_root(treeRoot)
        elif t== 'g':
            mg = group_pattern.match(f)
            """
            mg.group(1) id
            mg.group(2) down_count
            mg.group(3) up_count
            """
            gNode = Node(id = mg.group(1), parent = layer_dict[layer-1], node_type = 'g')
            layer_dict[layer] = gNode
            if mg.group(3) == '*':
                gNode.g_u = np.inf
            else:
                gNode.g_u = mg.group(3)
            gNode.g_d = mg.group(2)
            layer_dict[layer] = gNode
            gNode.parent.add_child(gNode)
        else:
            treeNode = Node(id = m.group(3), parent = layer_dict[layer-1], node_type = t)
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
        while(m.group(4)):
            cc = m.group(4)
            m = common_more_con_pattern.match(cc)
            li_pos.append(not bool(m.group(2)))
            literal.append(m.group(3))
        """
         con_id: constraint identifier
         literal: literals
         li_pos: whether is positive or each literals
        """
        con_stmt = Constraint(id = con_id, literals = literal, literals_pos = li_pos)
        ft.add_constraint(con_stmt)

    # pdb.set_trace()
    ft.set_features_list()

    return ft

# three objectives at this time
class FTModel(model):
    def __init__(self, url, name):
        self.name = name
        self.url = url
        self.ft = load_ft_url(url)
        dec = [Has(l.id,0,1) for l in self.ft.leaves]
        obj = [Has(name='fea', lo=0, hi=self.ft.featureNum-len(self.ft.groups), goal = gt),
               Has(name='conVio', lo=0,hi=len(self.ft.con), goal = lt),
               Has(name='cost', lo=0,)] #TODO
        model.__init__(self, dec, obj)

    def eval(self, c, doNorm=True):
        t = self.ft #abbr.
        sol = c.decs

        # obj1: features numbers
        # initialize the fulfill list
        fulfill = [-1] * t.featureNum
        for x in range(len(sol)):
            fulfill[t.features.index(t.leaves[x])] = sol[x]
        # fill other tree elements
        t.fillForm4AlFea(fulfill)
        #print fulfill
        # here group should not count as feature
        gsum = 0
        for g in t.groups:
            gsum += fulfill[t.features.index(g)]
        obj1 = sum(fulfill) - gsum

        # obj2: constraint violation
        obj2 = 0
        for cc in t.con:
            if cc.iscorrect(t,fulfill):
                obj2 += 1
        obj2 = len(t.con) - obj2
        c.scores = [obj1, obj2]

        if doNorm:
            self.normObjs(c)
        return c

    """
    checking whether the candidate meets ALL constraints
    """
    def ok(self,c):
        try:
            if c.scores == []:
                self.eval(c)
        except:
            self.eval(c)
        return c.scores[1] == 0

    def genRandomCan(self,guranteeOK = False):
        while True:
            randBinList = lambda n: [random.randint(0,1) for b in range(1,n+1)]
            can = candidate(decs=randBinList(len(self.dec)),scores=[])
            if not guranteeOK or self.ok(can): break
        return can

    def printModelInfo(self):
        print '---Information for SPL--------'
        print 'Name:', self.name
        print 'Leaves #:', len(self.ft.leaves)
        print 'Total Features#:', self.ft.featureNum-len(self.ft.groups)
        print 'Constraints#:', len(self.ft.con)
        print '-'*30

def main():
    m = FTModel('../feature_tree_data/cellphone.xml')
    can = m.genRandomCan()
    m.eval(can,doNorm=False)
    pdb.set_trace()

if __name__ == '__main__':
    main()




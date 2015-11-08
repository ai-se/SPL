import pdb
import os
import time
from Feature_tree import *
from parser import *
from copy import deepcopy
from random import *


# TESTING FOR ALL KINDS OF MUTATE ENGINES

class mutateEngine(object):
    def __init__(self, feature_tree):
        self.ft = feature_tree
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.getConsNum()
        self.con_repo = deepcopy(self.ft.con)

    def refresh(self):
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.getConsNum()
        self.con_repo = deepcopy(self.ft.con)

    def getFulfill(self, node):
        index =  self.ft.features.index(node)
        return self.fea_fulfill[index]

    def setFulfill(self, node, setting, checkConstraint = True):
        if not self.checkWhetherSet(node, setting): Exception('setting conflict')
        index = self.ft.features.index(node)
        self.fea_fulfill[index] = setting
        if checkConstraint:
            self.checkConstraints(node)

    @staticmethod
    def getShuffleList(list, cut = None):
        return sorted(list, key=os.urandom)[0:cut]

    def checkConstraints(self,setted_node):
        me = self.getFulfill(setted_node)
        for i,con in enumerate(self.con_repo):
            if self.con_fulfill[i]: continue
            if setted_node.id not in con.literals: continue
            if con.li_pos[con.literals.index(setted_node.id)] == me:
                self.con_fulfill[i] = 1
            else:
                con.literals.pop(i)
                con.li_pos.pop(i)
                if len(con) == 0:  raise Exception('constraint fail!')

    def checkWhetherSet(self, node, want):
        a = self.getFulfill(node)
        if a == -1: return True # not set before
        return a == want

    def mutateChild(self, node):
        me = self.getFulfill(node)
        #pdb.set_trace()
        if node.children == []: return
        if node.node_type == 'g': # the current node is a group
            if not me: map(lambda x:self.setFulfill(x,0), node.children)
                #For c in node.children: self.setFulfill(c,0)
            else:
                want = randint(node.g_d, node.g_u)
                exist_1 = len([c for c in node.children if self.getFulfill(c)==1])
                want = want-exist_1
                if want < 0: raise Exception('group fail!')
                for i,c in enumerate(self.getShuffleList(node.children)):
                    self.setFulfill(c, int(i<=want))
                    self.mutateChild(c)
            return
        if node.children[0].node_type == 'g': # my child is a group-> just to set as me
            c = node.children[0]
            self.setFulfill(c,me,Flase)
            self.mutateChild(c)
            return
        # the current node is root, mandory or optional
        m_child = [c for c in node.children if c.node_type == 'm']
        o_child = [c for c in node.children if c.node_type == 'o']
        shuffle(m_child)
        shuffle(o_child)
        #pdb.set_trace()
        if me:
            for m in m_child:
               self.setFulfill(m,1)
            for o in o_child:
                self.setFulfill(o,randint(0,1))
        if not me:
            if len(m_child) == 0:
                for o in o_child:
                    self.setFulfill(o,0)
            else:
                self.setFulfill(m_child[0],0)
                for other in m_child[1:]+o_child:
                    self.setFulfill(o, randint(0,1))
        return

    def generate(self, pop = 10):
        i = 0
        self.refresh()
        while True:
            try:
                self.setFulfill(self.ft.root, 1)
                self.mutateChild(self.ft.root)
                #print "mutate DONE!"
                i = i+1
                if i >= pop :return
            except:
                pass


for name in ['cellphone','eshop','webportal','eis']:
    m = FTModel('../feature_tree_data/'+name+'.xml', name, name+'.cost')
    m.printModelInfo()
    engine = mutateEngine(m.ft)
    start_time = time.time()
    engine.setFulfill(m.ft.root,1)
    engine.generate(10)
    print("--- %s seconds --- for 10 by new mutate engine" % (time.time() - start_time))
    start_time = time.time()
    for i in range(10):
        m.genRandomCan(guranteeOK=True)
    print("--- %s seconds --- for 10 by origin mutate engine" % (time.time() - start_time))


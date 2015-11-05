import pdb
import os
from Feature_tree import *
from random import *

# TESTING FOR ALL KINDS OF MUTATE ENGINES

class mutateEngine(object):
    def __init__(self, feature_tree):
        self.ft = feature_tree
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.getConsNum()

    def getFulfill(self, node):
        index =  self.ft.features.index(node)
        return self.fea_fulfill[index]

    def setFulfill(self, node, setting):
        index = self.ft.features.index(node)
        self.fea_fulfill[index] = setting

    @staticmethod
    def getShuffleList(list, cut = None):
        return sorted(list, key=os.urandom)[0:cut]

    def mutateChild(self, node):
        me = self.getFulfill(node)
        if node.children == []: return
        if node.type == 'g': # the current node is a group
            if not me: map(lambda x:self.setFulfill(x,0), node.children)
                #for c in node.children: self.setFulfill(c,0)
            else:
                want = randint(node.g_d, node.g_u)
                for i,c in enumerate(self.getShuffleList(node.children)):
                    self.setFulfill(c, int(i<=want))
            return

        if node.children[0].node_type == 'g': # my child is a group-> just to set as me
            self.setFulfill(node.children[0],me)
            #TODO cont.

        # the current node is mandory or optional
        m_child = [c for c in node.children if c.node_type == 'm']
        o_child = [c for c in node.children if c.node_type == 'o']
        shuffle(m_child)
        shuffle(o_child)

       # if node.type == 'o' and me: # the current node is optional
       if me:
            for m in m_child:
                self.setFulfill(m,1)
                #TODO cont.
            for o in o_child:
                self.setFulfill(o,randint(0,1))
                #TODO cont.

        #if node.type == 'o' and (not me): # current node is optional but failed
        if not me:
            if len(m_child) == 0:
                for o in o_child:
                    self.setFulfill(o,0)
                    #TODO cont.
            else:
                self.setFulfill(m_child[0],0)
                for other in m_child[1:]+o_child:
                    self.setFulfill(o, randint(0,1))
                    #TODO cont.

        #if node.type in ['m','r'] and me: # the current node is manadory



pdb.set_trace()

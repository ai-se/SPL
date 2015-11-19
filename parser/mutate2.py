import pdb,traceback,random
import os
import time
from Feature_tree import *
from parser import *
from copy import *
from random import *

# TESTING FOR ALL KINDS OF MUTATE ENGINES
# MUTATE WITH BACKTRACKING OF VARIABLES

class mutateEngine(object):
    def __init__(self, feature_tree):
        self.ft = feature_tree
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.getConsNum()
        self.temp_c = [0]*len(self.ft.features)
        self.tem_c_c = [0]*self.ft.getConsNum()
        self.con_repo = deepcopy(self.ft.con)

    def refresh(self):
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.getConsNum()
        self.con_repo = deepcopy(self.ft.con)

    def getFulfill(self, node):
        index =  self.ft.features.index(node)
        return self.fea_fulfill[index]

    def setFulfill(self, node, setting, checkConstraint = True):
        if not self.checkNeedSet(node, setting): return
        index = self.ft.features.index(node)
        self.fea_fulfill[index] = setting
        if checkConstraint:
            self.checkConstraints(node)

    """
    @staticmethod
    def getShuffleList(l, cut = 'notset'):
        l2 = copy(l)
        shuffle(l2)
        if cut != 'notset':
            return l2[0:cut]
        else:
            return l2
    """

    def checkConstraints(self,setted_node):
        me = self.getFulfill(setted_node)
        for i,con in enumerate(self.con_repo):
            if self.con_fulfill[i]: continue
            if setted_node.id not in con.literals: continue
            location = con.literals.index(setted_node.id)
            if con.li_pos[location] == me:
                self.con_fulfill[i] = 1
            else:
                con.literals.pop(location)
                con.li_pos.pop(location)

                if len(con.literals) == 1: #have a try for the last literal
                    last_i = self.ft.find_fea_index_by_id(con.literals[0])
                    self.setFulfill(self.ft.features[last_i], int(con.li_pos[0]))
                    self.con_fulfill[i] = 1
                if len(con.literals) == 0:
                    #print 'constraint fail coused by ' + setted_node.id + ' at constraint '+ str(i)
                    self.tem_c_c[i]+=1
                    raise Exception('constraint fail!')

    """
    set does the node need/CAN to be set as want
    if can't set, raise exception
    if not set, return true
    if setted, return false
    """
    def checkNeedSet(self, node, want):
        a = self.getFulfill(node)
        if a == -1: return True # not set before
        if a != want:
            index =  self.ft.features.index(node)
            self.temp_c[index] += 1
            raise Exception('setting conflict')
        else: return False

    def mutateChild(self, node):
        me = self.getFulfill(node)
        if node.children == []: return
        if node.node_type == 'g': # the current node is a group
            if not me:
                for c in node.children:
                    self.setFulfill(c,0)
                    self.mutateChild(c)
            else:
                want = randint(node.g_d, node.g_u)
                exist_1 = len([c for c in node.children if self.getFulfill(c)==1])
                want = want-exist_1
                if want < 0: raise Exception('group fail!')
                children = [c for c in node.children]
                shuffle(children)
                for c in children:
                    if want > 0:
                        try:
                            want -= 1
                            self.setFulfill(c, 1)
                            self.mutateChild(c)
                        except:
                            want += 1
                            try:
                                self.setFulfill(c,0)
                                self.mutateChild(c)
                            except:
                                #print "SPECIAL SI"
                                raise Exception
                    else:
                        self.setFulfill(c,0)
                        self.mutateChild(c)
                if want > 0: raise Exception('group fail!')
            return

        # the current node is root, mandory or optional
        m_child = [c for c in node.children if c.node_type in ['m','g']]
        o_child = [c for c in node.children if c.node_type == 'o']
        shuffle(m_child)
        shuffle(o_child)

        if me:
            # sepcial case
            if len(m_child)==0:
                for cc,o in enumerate(o_child):
                    self.setFulfill(o,1 if cc==0 else randint(0,1))
                    self.mutateChild(o)
                return

            for m in m_child:
               self.setFulfill(m,1)
               self.mutateChild(m)

            for o in o_child:
                self.setFulfill(o,randint(0,1))
                self.mutateChild(o)

        if not me:
            if len(m_child) == 0:
                for o in o_child:
                    self.setFulfill(o,0)
                    self.mutateChild(o)
            else:
                self.setFulfill(m_child[0],0)
                self.mutateChild(m_child[0])
                for other in m_child[1:]+o_child:
                    self.setFulfill(other, randint(0,1))
                    self.mutateChild(other)
        return

    def findLeavesFulfill(self, fulfill):
        r = []
        for x in self.ft.leaves:
            index = self.ft.features.index(x)
            r.append(fulfill[index])
        return r

    def genValidOne(self, returnFulfill = False):
        fulfill2return = []
        while True:
            try:
                self.refresh()
                self.setFulfill(self.ft.root,1)
                self.mutateChild(self.ft.root)
                fulfill2return = self.fea_fulfill
                leaves2return = self.findLeavesFulfill(fulfill2return)
                if returnFulfill: return fulfill2return, leaves2return
                else: return leaves2return
            except:
                #type, value, tb = sys.exc_info()
                #traceback.print_exc()
                #pdb.post_mortem(tb)
                pass

def comparePerformance():
    for name in ['cellphone','eshop','webportal','EIS']:
        m = FTModel('../feature_tree_data/'+name+'.xml', name, name+'.cost')
        m.printModelInfo()
        engine = mutateEngine(m.ft)
        start_time = time.time()
        for i in range(10): engine.genValidOne(True)
        print("--- %s seconds --- for 10 by new mutate engine" % (time.time() - start_time))
        continue
        start_time = time.time()
        for i in range(10):
            m.genRandomCan(guranteeOK=True)
        print("--- %s seconds --- for 10 by origin mutate engine" % (time.time() - start_time))


def unitTest(name):
    m = FTModel('../feature_tree_data/'+name+'.xml', name, name+'.cost')
    m.printModelInfo()
    engine = mutateEngine(m.ft)
    for i in range(100):
        print i
        a  = engine.genValidOne()
        can = candidate(decs = a)
        pdb.set_trace()
        if not  m.ok(can): pdb.set_trace()
    #pdb.set_trace()

if __name__ == '__main__':
    #comparePerformance()
    unitTest('eshop')

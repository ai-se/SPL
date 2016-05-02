from __future__ import division

import pdb
import time
from copy import deepcopy
from random import randint, shuffle

import FeatureModel
from __init__ import project_path
from candidatesMeasure import analysis_cans
from discoverer import Discoverer
from model import candidate

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


class MutateEngine(Discoverer):
    def __init__(self, feature_model):
        self.feature_model = feature_model
        self.ft = feature_model.ft
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.get_cons_num()
        self.temp_c = [0]*len(self.ft.features)
        self.tem_c_c = [0]*self.ft.get_cons_num()
        self.YESs = []
        self.NOs  = []
        self.con_repo = deepcopy(self.ft.con)

    def refresh(self):
        self.fea_fulfill = [-1] * len(self.ft.features)
        self.con_fulfill = [0] * self.ft.get_cons_num()
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
        shuffle(l2)d
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
                    last_i = self.ft.find_fea_index(con.literals[0])
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
            self.temp_c[index] += 1 if want == 0 else 0
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

    def gen_valid_one(self):
        while True:
            try:
                self.refresh()
                self.setFulfill(self.ft.root, 1)
                self.mutateChild(self.ft.root)
                fulfill2return = self.fea_fulfill
                leaves2return = self.findLeavesFulfill(fulfill2return)
                can = candidate(decs=leaves2return)
                can.fulfill = fulfill2return
                self.feature_model.eval(can)
                return can
            except:
                import traceback,sys
                type, value, tb = sys.exc_info()
                traceback.print_exc()
                # pdb.post_mortem(tb)
                pass

    def run(self, one_gen_time=20):
        GEN = 10

        stat_file_name = '{0}/Records/m2_{1}_{2}_stat.csv'.format(project_path, self.feature_model.name,
                                                                     time.strftime('%y%m%d'))
        stat_file = open(stat_file_name, 'w')
        stat_file.write('generation, generated_cans, valids, hypervolume, timestamp\n')
        t = time.time()
        for i in range(GEN):
            R = []
            while True:
                R.append(self.gen_valid_one())
                if time.time() - t > one_gen_time:
                    t = time.time()
                    hv = analysis_cans(R, False)
                    stat_file.write('{0},{1},{2},{3},{4}\n'.format(i, len(R), 1, hv, t))
                    stat_file.flush()
                    t = time.time()
                    print i
                    break
        stat_file.close()


def demo(name):
    import time
    time1 = time.time()

    m = FeatureModel.FeatureModel(name, setConVioAsObj=False)
    engine = MutateEngine(m)
    can = engine.gen_valid_one()
    pdb.set_trace()
    exit(0)
    engine.run()
    pdb.set_trace()

if __name__ == '__main__':
    name = ['eis']
    for n in name:
        demo(n)

import pdb, math, random
import numpy as np
from GALE import *

import os,sys
parserdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/parser/'
sys.path.insert(0,parserdir)
from parser import *

class BinGALE(GALE):

    def __init__(self, model, np=100):
        self.model = model # FTModel is needed (FTModel is a binary model for SPL)
        self.np = np # initial population size


    ##################################################
    # Canx  : candidate 1                            #
    # cany  : candidate 2                            #
    # return: distance of decs between candidate 1&2 #
    ##################################################
    def dist(self, canx,cany):
        x,y = canx.decs, cany.decs
        # definition to binary distance - Jaccard's distance
        # p: Y Y
        # q: Y N
        # r: N Y
        # s: N N
        p,q,r,s = 0,0,0,0
        for i in range(len(x)):
            if x[i] and y[i]: p += 1
            if x[i] and not y[i]: q += 1
            if not x[i] and y[i]: r += 1
            if not x[i] and not y[i]: s += 1
        return (0.0+ q+r)/(0.0 + p+q+r)


    def mutate1(self, old, c, east, west, gamma = 1.5, delta = 1):
        # east is better than the west
        if c == 0: return old
        new = o(decs=old.decs[:],scores=[]) #copy the decisions and omit the score
        for i,(e,w) in enumerate(zip(east.decs, west.decs)):
            if e == w:
                new.decs[i] = e
            elif random.random() < c:
                new.decs[i] = e
            else:
                new.decs[i] = w
        return new

def main_find_init_pop_passrate():
    eis = FTModel('../feature_tree_data/cellphone.xml','cellphone')
    bing = BinGALE(eis)
    bing.model.printModelInfo()
    count = 0
    tries = 500
    for i in range(tries):
        e = bing.model.genRandomCan(guranteeOK=False)
        if bing.model.ok(e): count += 1
    print 'initial pop pass rate:', count/float(tries)*100, '%'

    #eis = FTModel('../feature_tree_data/webportal.xml','web portal')
    #eis = FTModel('../feature_tree_data/eshop.xml','e-shop')

    #pdb.set_trace()
    #bing.gale()

    
if __name__ == '__main__':
    main_find_init_pop_passrate()

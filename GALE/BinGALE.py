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
        new = old[:]
        for i in range(len(old)):
            if east[i] == west[i]:
                new[i] = east[i]
            elif random.random() < c:
                new[i] = east[i]
            else:
                new[i] = west[i]
        return new


# def EISmodel():
#     print "=======EIS============"
#     m = parser.FMing('../feature_tree_data/EIS.xml')
#     gale = BinGALE(m.argD, m.objD,50,m.getObj)
#     x = gale.gale()
#     print x


if __name__ == '__main__':
    pdb.set_trace()
    pass

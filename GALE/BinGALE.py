import pdb,traceback, sys
import math, random
import numpy as np
from GALE_timing import *
import os,sys
parserdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/parser/'
sys.path.insert(0,parserdir)
from parser import *


class BinGALE(GALE):

    def __init__(self, model, np=100):
        self.model = model # FeatureModel is needed (FeatureModel is a binary model for SPL)
        self.np = np # initial population size
        self.time_ran_pop = 0
        self.time_where = 0
        self.time_mutate = 0

    ##################################################
    # Canx  : candidate 1                            #
    # cany  : candidate 2                            #
    # return: distance of decs between candidate 1&2 #
    ##################################################
    def dist(self, canx,cany):
        x,y = canx.decs, cany.decs
        """
        # definition to binary distance - Jaccard's distance
        # p: Y Y
        # q: Y N
        # r: N Y
        # s: N Ns
        if x == y: return 0
        p,q,r,s = 0,0,0,0
        for i in range(len(x)):
            if x[i] and y[i]: p += 1
            if x[i] and not y[i]: q += 1
            if not x[i] and y[i]: r += 1
            if not x[i] and not y[i]: s += 1
        return (0.0+ q+r)/(0.0 + p+q+r)
        """
        # Hamming distance
        return sum(ch1 != ch2 for ch1, ch2 in zip(x, y))

    ###################################
    # mutate for the binary variables #
    # TODO: new strategy              #
    ###################################
    def mutate1(self, old, c, east, west, gamma = 1.5, delta = 1):
        # east is better than the west
        if c == 0: return old
        new = o(decs=old.decs[:],fitness=[]) #copy the decisions and omit the score
        for i,(e,w) in enumerate(zip(east.decs, west.decs)):
            if e == w:
                new.decs[i] = e
            elif random() < c:
                new.decs[i] = e
            else:
                new.decs[i] = w
        return new

"""
def main_find_init_pop_passrate():
    eis = FeatureModel('../splot_data/cellphone.xml','cellphone')
    bingh = BinGALE(eis)
    bing.model.printModelInfo()
    count = 0
    tries = 500
    for i in range(tries):
        e = bing.model.genRandomCan(guranteeOK=False)
        if bing.model.ok(e): count += 1
    print 'initial pop pass rate:', count/float(tries)*100, '%'

    #eis = FeatureModel('../splot_data/webportal.xml','web portal')
    #eis = FeatureModel('../splot_data/eshop.xml','e-shop')

    #pdb.set_trace()
    #bing.gale()
"""

def main_gale_with_spl(name):
    m = FTModel('../splot_data/'+name+'.xml',name, name+'.cost')
    # gale
    import time
    t = time.time()
    bing = BinGALE(m,100)
    b = bing.gale()
    total_time = time.time()-t
    # print '---time info---'
    # print 'total time:', total_time*10
    # print 'random generated pop: ', round(bing.time_ran_pop/total_time*100,2), '%'
    # print 'where func: ',  round(bing.time_where/total_time*100,2), '%'
    # print 'mutate func: ', round(bing.time_mutate/total_time*100,2), '%'
    # print '---the end-----'
    #pdb.set_trace()

if __name__ == '__main__':
    try:
        #main_gale_with_spl('cellphone')
        #main_gale_with_spl('webportal')
        #main_gale_with_spl('eshop')
        main_gale_with_spl('eis')
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


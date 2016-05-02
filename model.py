import random

from o import *


def candidate(decs = [], fitness =[]):
    return o(decs=decs, fitness=fitness)

r = random.random
def within(lo,hi): return lo + (hi - lo)*r()
def lt(x,y): return x < y # less than
def gt(x,y): return x > y # larger than

class Has(object):
    def __init__(i,name='', lo=0, hi=1e32, init=0,
               goal=None,touch=True):
       i.name,i.lo,i.hi      = name,lo,hi
       i.init,i.goal,i.touch = init,goal,touch

    # WARNING: norm does not change the x
    def norm(i,x):
        return  round((x - i.lo) / (i.hi-i.lo+0.00001),2)


    def restrain(i,x):
       if   x < i.lo: return i.lo
       elif x > i.hi: return i.hi
       else: return x

    def any(i):
       return within(i.lo,i.hi)

    def ok(i,x):
       return i.lo <= x <= i.hi

    def __repr__(i):
       return '%s=%s' % (i.name, o(name=i.name,lo=i.lo,hi=i.hi,init=i.init,goal=i.goal,touch=i.touch))



class model(object):
    def __init__(i, dec=[], obj=[]):
        i.dec = dec # should be Has list
        i.obj = obj # should be Has list
        i.decNum = len(i.dec)
        i.objNum = len(i.obj)

    def objectives(i):
        assert False, 'Should implement in the subclass'

    def learn_base_line(i, tries = 10000):
        print '===== Start base line study ===='
        for o in i.obj: o.lo, o.hi = 1e32, -1e32
        for _ in range(tries):
            can = i.genRandomCan()
            i.eval(can,doNorm=False)
            for index, y in enumerate(can.fitness):
                if y > i.obj[index].hi: i.obj[index].hi = y
                if y < i.obj[index].lo: i.obj[index].lo = y
        print '===== Base line study done! ===='

    def normDecs(i,can):
        assert len(can.decs) == i.decNum
        for index,x in enumerate(can.decs):
            i.dec[index].norm(x)

    def normObjs(i, can):
        assert len(can.fitness) == i.objNum
        for index, f in enumerate(can.fitness):
            can.fitness[index] = i.obj[index].norm(f)

    def genRandomCan(i,guranteeOK = False):
        can = candidate(decs=[x.any() for x in i.dec])
        if guranteeOK:
            while True:
                if i.ok(can):break
                can = candidate(decs=[x.any() for x in i.dec])
        return can

    """
    def energy(i, scores):
        e = 0
        for o in range(i.objNum):
            e += (scores[o] - i.obj[o].lo) / (i.obj[o].hi-i.obj[o].lo)
        return e
    """

    def eval(i, c, doNorm=True):
        c.fitness = [obj(c) for obj in i.objectives()]
        if doNorm:
            i.normObjs(c)
        return c

    def ok(i, c):
        if c == None: return False # null candidate is not allowed
        # just check the dependent variables range. more costraints should be set up at the subclass
        for x in range(i.decNum):
            if not i.dec[x].ok(c.decs[x]): return False
        return True



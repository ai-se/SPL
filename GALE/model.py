import pdb, random, numpy
from o import *


def candidate(decs = [], scores =[]):
    return o(decs=decs, scores=scores)

r = random.random
def within(lo,hi): return lo + (hi - lo)*r()
def lt(x,y): return x < y # less than
def gt(x,y): return x > y # larger than

class Has(object):
    def __init__(i,name='',lo=0,hi=1e32,init=0,
               goal=None,touch=True):
       i.name,i.lo,i.hi      = name,lo,hi
       i.init,i.goal,i.touch = init,goal,touch

    # WARNING: norm does not change the x
    def norm(i,x):
        return  (x - i.lo) / (i.hi-i.lo+0.00001)


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
            for index, y in enumerate(can.scores):
                if y > i.obj[index].hi: i.obj[index].hi = y
                if y < i.obj[index].lo: i.obj[index].lo = y
        print '===== Base line study done! ===='

    def normDecs(i,can):
        assert len(can.decs) == i.decNum
        for index,x in enumerate(can.decs):
            i.dec[index].norm(x)

    def normObjs(i,can):
        assert len(can.scores) == i.objNum
        for index,f in enumerate(can.scores):
            can.scores[index] = i.obj[index].norm(f)

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
        c.scores = [obj(c) for obj in i.objectives()]
        if doNorm:
            i.normObjs(c)
        return c

    def ok(i, c):
        if c == None: return False # null candidate is not allowed
        # just check the dependent variables range. more costraints should be set up at the subclass
        for x in range(i.decNum):
            if not i.dec[x].ok(c.decs[x]): return False
        return True


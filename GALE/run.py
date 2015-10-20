from GALE import *

class Schaffer(object):
    def __init__(self):
        self.hi = [10**50]
        self.lo = [-10**50]
        self.argD = 1
        self.objD = 2

    def getObj(self,x):
        return [x[0]**2/100.0,(x[0]-2)**2/144.0]

    def validX(self,x):
        return x[0] >= -10**1 and x[0] <= 10**1

    def candidate(self, required = 1):
        s = []
        for t in range(required):
            x =[random.uniform(-10**1,10**1)]
            s.append(x)
        return s

class Square(object):
    def __init__(self):
        self.hi = [10]
        self.lo = [-10]
        self.argD = 1
        self.objD = 1

    def getObj(self,x):
        return [x[0]**2]

    def validX(self,x):
        return x[0] >= -10 and x[0] <= -10

    def candidate(self, required = 1):
        s = []
        for t in range(required):
            x = [random.randint(-10,10)]
            s.append(x)
        return s

def squareTest():
    q = Square()
    gengine = GALE(q.hi, q.lo, q.argD, q.objD, 100, q.getObj, q.validX, q.candidate)
    out = gengine.gale()
    print out

def schafferTest():
    s = Schaffer()
    gengine = GALE(s.hi, s.lo, s.argD, s.objD, 100, s.getObj, s.validX, s.candidate)
    #pdb.set_trace()
    out = gengine.gale()
    print out


def ZDTtest():
    z = ZDT4(5)
    hi = [1] + [5] * 4
    lo = [0] + [-5] * 4
    gengine = GALE(hi, lo, z.argD, z.objD, 50, z.getObj, z.vaildX, z.candidate)
    pdb.set_trace()
    out = gengine.gale()
    pdb.set_trace()
    print out


if __name__ == '__main__':
    #schafferTest()
    ZDTtest()
    pdb.set_trace()

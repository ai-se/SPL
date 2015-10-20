import pdb, math, random

# Definition for function ZDT4
class ZDT4(object):
    def __init__(self,argD = 10):
        self.argD = argD
        self.objD = 2

    def candidate(self, required = 1):
        s = []
        for t in range(required):
            x = []
            x.append(random.random())
            for i in range(1,self.argD):
                x.append(random.uniform(-5,5))
            s.append(x)
        return s

    def vaildX(self,x):
        if len(x) != self.argD:
            return False
        if x[0] < 0 or x[0] > 1:
            return False
        for i in range(1,self.argD):
            if x[i] < -5 or x[i] > 5:
                return False
        return True

    def getObj(self,x):
        g = 0
        for i in range(1,self.argD):
            g += x[i]**2 - 10 * math.cos(4 * math.pi * x[i])
        g += 1 + 10 * (self.argD - 1)
        return [x[0], g * ( 1 - ( x[0] / g) **2 )/500 ]

def test():
    z = ZDT4()
    sol = z.candidate(5)
    for p in sol:
        print z.getObj(p)


if __name__ == '__main__':
    test()
    

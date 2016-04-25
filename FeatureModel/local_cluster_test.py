from os import sys, path

from ftmodel import FTModel

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from model import candidate


def binaryCandidate(num, decSize):
    d = [int(x) for x in bin(num)[2:]]
    for i in range(decSize-len(d)): d.insert(0,0)
    return candidate(decs=d)


def test(name):
    model = FTModel(name)
    n = len(model.dec)
    print n
    with open('temp_node.csv', 'w') as f:
        for i in range(2**n):
            if model.ok(binaryCandidate(i, n)):
                f.write(str(i))
                f.write('\n')
            if i % 10000 == 0:
                print i


if __name__ == '__main__':
   # test('cellphone')
    test('webportal')

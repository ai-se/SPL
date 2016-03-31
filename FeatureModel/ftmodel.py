import pdb
import mutate2  # v2 mutate engine
from parser import load_ft_url
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from GALE.model import *

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.1"
__email__ = "jchen37@ncsu.edu"


class FTModel(model):
    def __init__(self, name, num_of_attached_objs=2, setConVioAsObj=True):
        self.name = name

        spl_addr = [i for i in sys.path if i.endswith('SPL')][0]
        url = spl_addr + '/feature_tree_data/' + self.name + '.xml'
        self.url = url
        self.ft = load_ft_url(url)

        self.ft.load_cost(name)
        self.ft.load_time(name)
        dec = [Has(l.id, 0, 1) for l in self.ft.leaves]

        obj = [Has(name='fea', lo=0, hi=self.ft.featureNum - len(self.ft.groups), goal=lt)]  # number of NOT included features
        if setConVioAsObj:
            obj.append(Has(name='conVio', lo=0, hi=len(self.ft.con), goal=lt))
        if num_of_attached_objs >= 1:
            obj.append(Has(name='cost', lo=0, hi=sum(self.ft.cost), goal=lt))
        if num_of_attached_objs >= 2:
            obj.append(Has(name='time', lo=0, hi=sum(self.ft.time), goal=lt))

        self.eval_count = 0

        self.mutateEngine2 = mutate2.mutateEngine(self.ft)  # TODO setting the mutate engine!!!
        pdb.set_trace()
        self.mutateEngines = []

        model.__init__(self, dec, obj)

    def eval(self, candidate, doNorm=True, returnFulfill=False):
        self.eval_count += 1
        t = self.ft  # abbr.
        sol = candidate.decs

        # obj1: features numbers
        # initialize the fulfill list
        fulfill = [-1] * t.featureNum
        for i, l in zip(sol, t.leaves):
            fulfill[t.features.index(l)] = i

        # fill other tree elements
        t.fill_form4all_fea(fulfill)

        # here group should not count as feature
        gsum = 0
        for g in t.groups:
            gsum += fulfill[t.features.index(g)]
        obj1 = len(t.features)-len(t.groups) - (sum(fulfill) - gsum)  # LESS IS MORE!
        candidate.scores = [obj1]

        # constraint violation
        if [o for o in self.obj if o.name == 'conVio']:
            conVio = len(t.con)
            for cc in t.con:
                if cc.is_correct(t, fulfill):
                    conVio -= 1
            candidate.scores.append(conVio)

        # total cost
        if [o for o in self.obj if o.name == 'cost']:
            total_cost = 0
            for i, f in enumerate(t.features):
                if fulfill[i] == 1 and f.node_type != 'g':
                    total_cost += t.cost[i]
            candidate.scores.append(total_cost)

        # total time
        if [o for o in self.obj if o.name == 'time']:
            total_time = 0
            for i, f in enumerate(t.features):
                if fulfill[i] == 1 and f.node_type != 'g':
                    total_time += t.time[i]
            candidate.scores.append(total_time)

        if doNorm:
            self.normObjs(candidate)

        # store the fulfill for convenience
        candidate.fulfill = fulfill

        if returnFulfill:
            return fulfill
        else:
            return None

    """
    checking whether the candidate meets ALL constraints
    """

    def ok(self, c):
        if not hasattr(c, 'scores'):
            self.eval(c)
        elif not c.scores:
            self.eval(c)

        return c.scores[1] == 0 and c.fulfill[0] == 1

    # def genRandomCanBrute(self, guranteeOK = False):
    #     import random
    #     while True:
    #         randBinList = lambda n: [random.choice([0, 1]) for _ in range(n)]
    #         can = candidate(decs=randBinList(len(self.dec)), scores=[])
    #         if not guranteeOK or self.ok(can): break
    #     return can

    """
    Applying v2 mutate engine
    """

    def genRandomCan(self, guranteeOK=False):
        return candidate(decs=self.mutateEngine2.genValidOne(), scores=[])

    def printModelInfo(self):
        print '---Information for SPL--------'
        print 'Name:', self.name
        print 'Leaves #:', len(self.ft.leaves)
        print 'Total Features #:', self.ft.featureNum - len(self.ft.groups)
        print 'Constraints#:', len(self.ft.con)
        print '-' * 30


def main(name):
    m = FTModel(name, setConVioAsObj=False)
    m.printModelInfo()
    can = m.genRandomCan(guranteeOK=True)
    m.ok(can)
    # m.eval(can,doNorm=False)
    pdb.set_trace()


if __name__ == '__main__':
    main('eshop')

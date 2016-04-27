from os import sys, path

import bruteDiscover
import mutate2  # v2 mutate engine
from parser import load_ft_url

# import optima.problems.problem
import ecspy.benchmarks
import pdb
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from model import *

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
        dec = [Has(l.id, 0, 1) for l in self.ft.features]
        # number of NOT included features
        obj = [Has(name='fea', lo=0, hi=self.ft.featureNum, goal=lt)]
        if setConVioAsObj:
            obj.append(Has(name='conVio', lo=0, hi=len(self.ft.con)+1, goal=lt))
        if num_of_attached_objs >= 1:
            obj.append(Has(name='cost', lo=0, hi=sum(self.ft.cost), goal=lt))
        if num_of_attached_objs >= 2:
            obj.append(Has(name='time', lo=0, hi=sum(self.ft.time), goal=lt))

        self.mutateEngines = {
            'brute': bruteDiscover.BruteDiscoverer(self),
            'v2': mutate2.MutateEngine(self),
        }

        model.__init__(self, dec, obj)

    def __repr__(self):
        s = '---Information for SPL--------\n'
        s += 'Name:%s\n' % self.name
        s += 'Leaves #:%d\n' % len(self.ft.leaves)
        s += 'Total Features #:%d\n' % (self.ft.featureNum - len(self.ft.groups))
        s += 'Constraints#:%d\n' % len(self.ft.con)
        s += '-' * 30
        s += '\n'
        return s

    def eval(self, candidate, doNorm=True, returnFulfill=False, checkTreeStructure=False):
        t = self.ft  # abbr.
        fulfill = candidate.decs

        obj1 = len(t.features) - sum(fulfill)  # LESS IS MORE!
        candidate.fitness = [obj1]

        # constraint violation
        conVio = len(t.con) + 1
        for cc in t.con:
            if cc.is_correct(t, fulfill):
                conVio -= 1

        # another import constraint, the feature tree structure!
        if checkTreeStructure:
            if self.ft.check_fulfill_valid(fulfill):
                candidate.correct_ft = True
                conVio -= 1
            else:
                candidate.correct_ft = False
        else:
            conVio -= 1

        all_obj_names = [o.name for o in self.obj]
        if 'conVio' in all_obj_names:
            candidate.fitness.append(conVio)
        candidate.conVio = conVio

        # total cost
        if 'cost' in all_obj_names:
            total_cost = 0
            for i, f in enumerate(t.features):
                if fulfill[i] == 1:
                    total_cost += t.cost[i]
            candidate.fitness.append(total_cost)

        # total time
        if 'time' in all_obj_names:
            total_time = 0
            for i, f in enumerate(t.features):
                if fulfill[i] == 1:
                    total_time += t.time[i]
            candidate.fitness.append(total_time)

        if doNorm:
            self.normObjs(candidate)

        if returnFulfill:
            return fulfill
        else:
            return None

    """
    checking whether the candidate meets ALL constraints
    """

    def ok(self, c, con_vio_tol=0):
        if not hasattr(c, 'scores'):
            self.eval(c)
        elif not c.fitness:
            self.eval(c)

        if not hasattr(c, 'correct_ft'):
            c.correct_ft = self.ft.check_fulfill_valid(c.decs)

        if not c.correct_ft:
            return False
        else:
            return c.conVio <= con_vio_tol

    def genRandomCan(self, engine_version):
        """
        when engine_version == 'random_sample', then generate any sample regardless the validness.
        """

        if engine_version == 'random_sample':
            engine = self.mutateEngines['brute']
            return engine.gen_valid_one(valid_sure=False)

        engine = self.mutateEngines[engine_version]
        return engine.gen_valid_one()

    def genRandomTree(self):
        """get candidates which meets the tree structure. ignore the constraints"""
        def rand_ones(lstLen, onesNum):
            result = [0] * lstLen
            l = range(lstLen)
            random.shuffle(l)
            for i in l[0:onesNum]:
                result[i] = 1
            return result

        def genNode(node, fulfill):
            checked = fulfill[self.ft.find_fea_index(node)]
            if checked == 0:
                self.ft.fill_subtree_0(node, fulfill)
                return fulfill

            if not node.children:
                return fulfill

            if node.node_type is not 'g':
                for c in node.children:
                    if c.node_type is 'o':
                        fulfill[self.ft.find_fea_index(c)] = random.choice([0,1])
                    else:
                        fulfill[self.ft.find_fea_index(c)] = 1
                child_sum = sum(fulfill[self.ft.find_fea_index(c)] for c in node.children)
                if child_sum == 0:
                    fulfill[self.ft.find_fea_index(random.choice(node.children))] = 1
            else:  # deal with the groups
                s_num = random.randint(node.g_d, node.g_u)
                lst = rand_ones(len(node.children), s_num)
                for l, c in zip(lst, node.children):
                    fulfill[self.ft.find_fea_index(c)] = l

            for c in node.children:
                genNode(c, fulfill)
            return fulfill

        fulfill = [0] * self.decNum
        fulfill[0] = 1
        decs = genNode(self.ft.root, fulfill)
        return o(decs=decs, correct_ft=True)

"""
#########
Translate the FTModel into escpy library defined Benchmark model.
"""


class EcsFTModel(ecspy.benchmarks.Binary):
    def __init__(self, ftmodel):
        self.ftmodel = ftmodel
        self.dimension_bits=1
        dimensions = ftmodel.decNum
        objectives = ftmodel.objNum
        ecspy.benchmarks.Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError(
                'dimensions (%d) must be greater than or equal to objectives (%d)' % (dimensions, objectives))
        self.bounder = ecspy.ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            passed_candidate = o(decs=c)
            self.ftmodel.eval(passed_candidate, doNorm=True, returnFulfill=False)
            fit = passed_candidate.fitness
            # if fit[1] != 0:
            #     fit = [1] * len(fit)
            fitness.append(ecspy.emo.Pareto(fit))
        return fitness

    @staticmethod
    def ecs_individual2ft_candidate(ecsi):
        return o(decs=ecsi.candidate, fitness=ecsi.fitness)


"""
######
Translate the FTModel into optima library
"""


# class OptimaFTModel(optima.problems.problem.Problem):
#     def __init__(self, ftmodel):
#         optima.problems.problem.Problem.__init__(self)
#         self.ftmodel = ftmodel
#         self.name = ftmodel.name
#
#         self.decisions = []
#         for d in range(self.ftmodel.decNum):
#             od = optima.problems.problem.Decision('x'+str(d), 0, 1)
#             self.decisions.append(od)
#
#         self.objectives = []
#         for o in self.ftmodel.obj:
#             oo = optima.problems.problem.Objective(o.name, o.lo, o.hi)
#             self.objectives.append(oo)
#
#     def evaluate(self, decisions):
#         decisions = map(lambda x:int(bool(x >= 0.5)), decisions)
#         c = o(decs=decisions)
#         self.ftmodel.eval(c, doNorm=True, returnFulfill=False)
#         return c.scores
#
#     def get_pareto_front(self):
#         raise NotImplementedError


def demo(name):
    m = FTModel(name, setConVioAsObj=True)
    pdb.set_trace()
    return


    test_m = EcsFTModel(m)
    problem = test_m
    ea = ecspy.ec.GA(random.Random())
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=100,
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          max_evaluations=300,
                          num_elites=6)
    pdb.set_trace()
    print m

    can = m.genRandomCan('v2')
    print m.ok(can)
    # m.eval(can,doNorm=False)
    pdb.set_trace()

if __name__ == '__main__':
    # demo('eshop')
    # demo('eis')
    # demo('webportal')
    demo('cellphone')
    # demo('fmtest')
    # demo('billing')
    # demo('greencar')
    # demo('marketplace')
    # demo('classicshell')
    # demo('carselection')

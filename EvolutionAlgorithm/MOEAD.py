from __future__ import print_function, division
import sys, os

from math import cos, pi

sys.path.append(os.path.abspath("."))
from NSGA3 import cover, DIVISIONS, rand_one
import matplotlib.pyplot as plt
import time
import random
import pdb

GENS = 400
REPEATS = 5
PI = pi


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


"""
:return
  -1 indicates worse
  0 indicates equal
  1 indicates better
"""


def compare(one, two, minimize=True):
    if one == two:
        return 0
    if minimize:
        status = 1 if one < two else -1
    else:
        status = 1 if one > two else -1
    return status


def norm(x, low, high):
    """
    Method to normalize value
    between 0 and 1
    """
    nor = (x - low) / (high - low + EPS)
    if nor > 1:
        return 1
    elif nor < 0:
        return 0
    return nor


def de_norm(x, low, high):
    """
    Method to de-normalize value
    between low and high
    """
    de_nor = x * (high - low) + low
    if de_nor > high:
        return high
    elif de_nor < low:
        return low
    return de_nor


def uniform(low, high):
    return random.uniform(low, high)


def default_settings():
    """
    Default MOEA/D settings
    """
    return O(
        pop_size=91,  # Size of Population
        gens=GENS,  # Number of generations
        distance="pbi",  # Distance metric
        T=20,  # Closest weight vectors.
        penalty=5,  # Penalty parameter for PBI distance
        crossover="sbx",  # Crossover Metric
        cr=1,  # Crossover rate for SBX
        nc=20,  # eta for SBX
        nm=20,  # eta for Mutation
        de_np=0.9,  # DE neighborhood probability
        de_cr=0.5  # DE crossover rate
    )


def get_time():
    return time.clock()


def eucledian(one, two):
    dist = 0
    for o_i, t_i in zip(one, two):
        dist += (o_i - t_i) ** 2
    return dist ** 0.5


def get_distance(distance_name):
    if distance_name == "tch":
        return weighted_tch
    elif distance_name == "pbi":
        return pbi
    assert False, "Invalid distance type : %s" % distance_name


"""
Distance Measures
"""


def pbi(moead, objectives, weights):
    """
    Penalty Boundary Intersection distance
    :param moead - Instance of MOEAD.
    :param objectives - Objectives of the point.
    :param weights - Weight of the points.
    """
    d1_vector = [abs(i - f) for i, f in zip(objectives, moead.ideal)]
    weights_norm = vector_norm(weights)
    d1 = dot_product(d1_vector, weights) / weights_norm
    d2_vector = []
    for i, obj in enumerate(moead.problem.objectives):
        if obj.to_minimize:
            d2_vector.append(objectives[i] - (moead.ideal[i] + d1 * weights[i]))
        else:
            d2_vector.append(objectives[i] - (moead.ideal[i] - d1 * weights[i]))
    d2 = vector_norm(d2_vector)
    return d1 + moead.settings.penalty * d2


def weighted_tch(moead, objectives, weights):
    """
    Tchebyshev distance
    :param moead - Instance of MOEAD.
    :param objectives - Objectives of the point.
    :param weights - Weight of the points.
    """
    mins = [sys.maxint] * len(moead.problem.objectives)
    maxs = [-sys.maxint] * len(moead.problem.objectives)
    for i in xrange(len(moead.problem.objectives)):
        for j in xrange(len(moead.problem.objectives)):
            val = moead.best_boundary_objectives[j][j]
            if val > maxs[i]: maxs[i] = val
            if val < mins[i]: mins[i] = val
        if maxs[i] == mins[i]:
            # print("min value and max value are the same")
            return sys.maxint
    dist = -sys.maxint
    for i in xrange(len(moead.problem.objectives)):
        normalized = abs((objectives[i] - moead.ideal[i]) / (maxs[i] - mins[i]))
        if weights[i] == 0:
            normalized *= 0.0001
        else:
            normalized *= weights[i]
        dist = max(dist, normalized)
    assert dist >= 0, "Distance can't be less than 0"
    return dist


"""
Utility Methods
"""


def vector_norm(vector):
    """
    Get the  norm of the vector
    :param vector: Vector to be normalized
    :return:
    """
    return sum([v ** 2 for v in vector]) ** 0.5


def dot_product(one, two):
    """
    Dot Product between one and two
    :param one: Vector one
    :param two: Vector two
    :return:
    """
    assert len(one) == len(two), "Vectors are not of equal length"
    return sum([o_i * t_i for o_i, t_i in zip(one, two)])


def get_crossover(name):
    if name == "sbx":
        return simulated_binary_crossover
    elif name == "de":
        return differential_evolution
    assert False, "Invalid Crossover type : %s" % name


SBX_CR = 1
SBX_ETA = 30
PM_ETA = 20
EPS = 0.000001


def sbx(problem, mom, dad, **params):
    """
    Simulated Binary Crossover Between Mummy And Daddy.
    Produces Sister and Brother.
    cr - Crossover Rate
    eta - Size of population used for distribution
    """
    cr = params.get("cr", SBX_CR)
    eta = params.get("eta", SBX_ETA)
    sis = mom[:]
    bro = dad[:]
    if random.random() > cr: return mom, dad
    for i, decision in enumerate(problem.decisions):
        if random.random() > 0.5:
            sis[i], bro[i] = bro[i], sis[i]
            continue
        if abs(mom[i] - dad[i]) <= EPS:
            continue
        low = problem.decisions[i].low
        up = problem.decisions[i].high
        small = min(sis[i], bro[i])
        large = max(sis[i], bro[i])
        some = random.random()

        # sis
        beta = 1.0 + (2.0 * (small - low) / (large - small))
        alpha = 2.0 - beta ** (-1 * (eta + 1.0))
        if some <= (1.0 / alpha):
            betaq = (some * alpha) ** (1.0 / (eta + 1.0))
        else:
            betaq = (1.0 / (2.0 - some * alpha)) ** (1.0 / (eta + 1.0))
        sis[i] = 0.5 * ((small + large) - betaq * (large - small))
        sis[i] = max(low, min(sis[i], up))

        # bro
        beta = 1.0 + (2.0 * (up - large) / (large - small))
        alpha = 2.0 - beta ** (-1 * (eta + 1.0))
        if some <= (1.0 / alpha):
            betaq = (some * alpha) ** (1.0 / (eta + 1.0))
        else:
            betaq = (1.0 / (2.0 - some * alpha)) ** (1.0 / (eta + 1.0))
        bro[i] = 0.5 * ((small + large) + betaq * (large - small))
        bro[i] = max(low, min(bro[i], up))
        if random.random() > 0.5:
            sis[i], bro[i] = bro[i], sis[i]
    return sis, bro


"""
Mutation Methods
"""


def simulated_binary_crossover(moead, point, population):
    """
    Perform Simulated Binary Crossover
    for producing mutants
    :param moead: Instance of MOEAD
    :param point: Instance of MOEADPoint to generate a crossover
    :param population: Population to search from
    :return: List containing Decisions of mutant
    """
    one = rand_one(point.neighbor_ids)
    two = rand_one(point.neighbor_ids)
    while one != two:
        two = rand_one(point.neighbor_ids)
    mom = population[one].decisions
    dad = population[two].decisions
    child, _ = sbx(moead.problem, mom, dad, cr=moead.settings.cr, eta=moead.settings.nc)
    return child


def differential_evolution(moead, point, population):
    """
    Use Differential Evolution to
    produce mutants
    :param moead: Instance of MOEAD
    :param point: Instance of MOEADPoint to generate a crossover
    :param population: Population to search from
    :return: List containing Decisions of mutant
    """
    problem = moead.problem
    rnd = random.random()
    if rnd < moead.settings.de_np:
        is_local = True
        moead.neighborhood = "local"
    else:
        is_local = False
        moead.neighborhood = "global"
    mom, dad = select_mates(point, population, is_local)
    me = point.decisions
    mom = population[mom].decisions
    dad = population[dad].decisions
    new = [None] * len(problem.decisions)
    for i, dec in enumerate(problem.decisions):
        new[i] = me[i] + moead.settings.de_cr * (dad[i] - mom[i])
        if new[i] < dec.low:
            new[i] = dec.low + random.random() * (me[i] - dec.low)
        if new[i] > dec.high:
            new[i] = dec.high - random.random() * (dec.high - me[i])
    return new


"""
Utility Methods
"""


def select_mates(point, population, is_local):
    """
    Select mates to perform DE
    :param point:
    :param population:
    :param is_local:
    :return: two mates for mating
    """
    seen = [point.id]

    def one_more(ids):
        one = rand_one(ids)
        while one not in seen:
            one = rand_one(ids)
            seen.append(one)
        return one

    neighbor_ids = point.neighbor_ids if is_local else population.keys()
    mom = one_more(neighbor_ids)
    dad = one_more(neighbor_ids)
    return mom, dad


def shuffle(lst):
    random.shuffle(lst)
    return lst


class O:
    def __init__(self, **d): self.has().update(**d)

    def has(self): return self.__dict__

    def update(self, **d): self.has().update(d); return self

    def __repr__(self):
        show = [':%s %s' % (k, self.has()[k])
                for k in sorted(self.has().keys())
                if k[0] is not "_"]
        txt = ' '.join(show)
        if len(txt) > 60:
            show = map(lambda x: '\t' + x + '\n', show)
        return '{' + ' '.join(show) + '}'

    def __getitem__(self, item):
        return self.has().get(item)


class Point(O):
    id = 0

    def __init__(self, decisions, problem=None):
        """
        Represents a point in the frontier for NSGA
        :param decisions: Set of decisions
        :param problem: Instance of the problem
        """
        O.__init__(self)
        Point.id += 1
        self.id = Point.id
        self.decisions = decisions[:]
        if problem:
            self.objectives = problem.evaluate(decisions)
            self.norm_objectives = problem.norm(self.objectives)
        else:
            self.objectives = []
            self.norm_objectives = []

    def clone(self):
        """
        Method to clone a point
        :return:
        """
        new = Point(self.decisions)
        new.objectives = self.objectives[:]
        new.norm_objectives = self.norm_objectives[:]
        return new

    def evaluate(self, problem, stat=None, gen=None):
        """
        Evaluate a point
        :param problem: Problem used to evaluate
        """
        if not self.objectives:
            self.objectives = problem.evaluate(self.decisions)
            self.norm_objectives = problem.norm(self.objectives)
            if stat:
                stat.evals += 1
                if gen is not None:
                    if stat.gen_evals is None:
                        stat.gen_evals = []
                    if len(stat.gen_evals) == gen:
                        stat.gen_evals[gen - 1] += 1
                    else:
                        stat.gen_evals.append(1)


class MOEADPoint(Point):
    def __init__(self, decisions, problem=None):
        """
        Represents a point in the frontier for MOEA/D
        :param decisions: list of decisions
        :param problem: Instance of problem
        :return:
        """
        Point.__init__(self, decisions, problem)
        self.wt_indices = None
        self.weight = None
        self.neighbor_ids = None

    def clone(self):
        """
        Method to clone a point
        :return:
        """
        new = MOEADPoint(self.decisions)
        if self.objectives: new.objectives = self.objectives[:]
        if self.wt_indices: new.wt_indices = self.wt_indices[:]
        if self.weight: new.weight = self.weight[:]
        if self.neighbor_ids: new.neighbor_ids = self.neighbor_ids[:]
        return new


def poly_mutate(problem, one, **params):
    """
    Perform Polynomial Mutation on a point.
    Default Mutation Probability = 1/No of Decisions in Problem
    """
    pm = params.get("pm", 1 / len(problem.decisions))
    eta = params.get("eta", PM_ETA)
    mutant = [0] * len(problem.decisions)

    for i, decision in enumerate(problem.decisions):
        if random.random() > pm:
            mutant[i] = one[i]
            continue

        low = problem.decisions[i].low
        high = problem.decisions[i].high
        del1 = (one[i] - low) / (high - low)
        del2 = (high - one[i]) / (high - low)

        mut_pow = 1 / (eta + 1)
        rand_no = random.random()

        if rand_no < 0.5:
            xy = 1 - del1
            val = 2 * rand_no + (1 - 2 * rand_no) * (xy ** (eta + 1))
            del_q = val ** mut_pow - 1
        else:
            xy = 1 - del2
            val = 2 * (1 - rand_no) + 2 * (rand_no - 0.5) * (xy ** (eta + 1))
            del_q = 1 - val ** mut_pow
        mutant[i] = max(low, min(one[i] + del_q * (high - low), high))
    return mutant


def convergence(obtained, ideals):
    """
    :param obtained - Obtained set of pareto solutions
    :param ideals - Ideal Pareto Frontier
    Calculate the convergence metric with
    respect to ideal solutions
    """
    if ideals is None:
        return None
    gammas = []
    for o in obtained:
        gammas.append(min([eucledian(o, ideal) for ideal in ideals]))
    return sum(gammas) / len(gammas)


def sort_solutions(solutions):
    """
    Sort a list of list before computing diversity
    """

    def sorter(lst):
        m = len(lst)
        weights = reversed([10 ** i for i in xrange(m)])
        return sum([element * weight for element, weight in zip(lst, weights)])

    return sorted(solutions, key=sorter)


def diversity(obtained, ideals):
    """
    Calculate the diversity (a.k.a spread)
    for a set of solutions
    """
    if ideals is None:
        return
    s_obtained = sort_solutions(obtained)
    s_ideals = sort_solutions(ideals)

    def closest(one, many):
        min_dist = sys.maxint
        closest_point = None
        for this in many:
            dist = eucledian(this, one)
            if dist < min_dist:
                min_dist = dist
                closest_point = this
        return min_dist, closest_point

    d_f = closest(s_ideals[0], s_obtained)[0]
    d_l = closest(s_ideals[-1], s_obtained)[0]
    distances = []
    for i in range(len(s_obtained) - 1):
        distances.append(eucledian(s_obtained[i], s_obtained[i + 1]))
    d_bar = sum(distances) / len(distances)
    d_sum = sum([abs(d_i - d_bar) for d_i in distances])
    delta = (d_f + d_l + d_sum) / (d_f + d_l + (len(s_obtained) - 1) * d_bar)
    return delta


def gt(a, b): return a > b


def lt(a, b): return a < b


def gte(a, b): return a >= b


def lte(a, b): return a <= b


class HyperVolume:
    """
    Hypervolume computation based on variant 3 of the algorithm in the paper:
    C. M. Fonseca, L. Paquete, and M. Lopez-Ibanez. An improved dimension-sweep
    algorithm for the hypervolume indicator. In IEEE Congress on Evolutionary
    Computation, pages 1157-1163, Vancouver, Canada, July 2006.
    Minimization is implicitly assumed here!
    """

    def __init__(self, reference):
        self.reference = reference
        self.list = None

    def compute(self, front):
        """
        Returns the hyper-volume that is dominated by a non-dominated front.
        Before the HV computation, front and reference point are translated, so
        that the reference point is [0, ..., 0].
        :param front:
        :return: hyper-volume value
        """

        def weak_dominate(one, two):
            """
            Check if one dominates two
            :param one: First set of objectives
            :param two: Second set of objectives
            :return:
            """
            for i in xrange(len(one)):
                if one[i] > two[i]:
                    return False
            return True

        relevants = []
        reference = self.reference
        d = len(reference)
        for point in front:
            if weak_dominate(point, reference): relevants.append(point)

        if any(reference):
            for j in xrange(len(relevants)):
                relevants[j] = [relevants[j][i] - reference[i] for i in xrange(d)]
        self.pre_process(relevants)
        bounds = [-1.0e308] * d
        return self.recurse(d - 1, len(relevants), bounds)

    def recurse(self, d, length, bounds):
        """
        Recursive call for hyper volume calculation.
        In contrast to the paper, the code assumes that the reference point
        is [0, ..., 0]. This allows the avoidance of a few operations.
        :param d: Dimension Index
        :param length: Number of relevant points
        :param bounds: Bounding Values
        :return: hyper-volume
        """
        hvol = 0.0
        sentinel = self.list.sentinel
        if length == 0:
            return hvol
        elif d == 0:
            # Single Dimension
            return -sentinel.next[0].value[0]
        elif d == 1:
            # 2 dimensional problem
            q = sentinel.next[1]
            h = q.value[0]
            p = q.next[1]
            while p is not sentinel:
                p_value = p.value
                hvol += h * (q.value[1] - p_value[1])
                if p_value[0] < h:
                    h = p_value[0]
                q = p
                p = q.next[1]
            hvol += h * q.value[1]
            return hvol
        else:
            remove = MultiList.remove
            reinsert = MultiList.reinsert
            recurse = self.recurse
            p = sentinel
            q = p.prev[d]
            while q.value is not None:
                if q.ignore < d:
                    q.ignore = 0
                q = q.prev[d]
            q = p.prev[d]
            while length > 1 and (q.value[d] > bounds[d] or q.prev[d].value[d] >= bounds[d]):
                p = q
                remove(p, d, bounds)
                q = p.prev[d]
                length -= 1
            q_area = q.area
            q_value = q.value
            q_prev_d = q.prev[d]
            if length > 1:
                hvol = q_prev_d.volume[d] + q_prev_d.area[d] * (q_value[d] - q_prev_d.value[d])
            else:
                q_area[0] = 1
                q_area[1:d + 1] = [q_area[i] * -q_value[i] for i in xrange(d)]
            q.volume[d] = hvol
            if q.ignore >= d:
                q_area[d] = q_prev_d.area[d]
            else:
                q_area[d] = recurse(d - 1, length, bounds)
                if q_area[d] < q_prev_d.area[d]:
                    q.ignore = d
            while p is not sentinel:
                p_value_d = p.value[d]
                hvol += q.area[d] * (p_value_d - q.value[d])
                bounds[d] = p_value_d
                reinsert(p, d, bounds)
                length += 1
                q = p
                p = p.next[d]
                q.volume[d] = hvol
                if q.ignore >= d:
                    q.area[d] = q.prev[d].area[d]
                else:
                    q.area[d] = recurse(d - 1, length, bounds)
                    if q.area[d] <= q.prev[d].area[d]:
                        q.ignore = d
            hvol - q.area[d] * q.value[d]
            return hvol

    def pre_process(self, front):
        d = len(self.reference)
        multi_list = MultiList(d)
        nodes = [MultiList.Node(d, point) for point in front]
        for i in xrange(d):
            HyperVolume.dimension_sort(nodes, i)
            multi_list.extend(nodes, i)
        self.list = multi_list

    @staticmethod
    def dimension_sort(nodes, i):
        decorated = [(node.value[i], node) for node in nodes]
        decorated.sort()
        nodes[:] = [node for (_, node) in decorated]

    @staticmethod
    def get_reference_point(problem, points):
        reference = [-sys.maxint if obj.to_minimize else sys.maxint for obj in problem.objectives]
        for point in points:
            for i, obj in enumerate(problem.objectives):
                if obj.to_minimize:
                    if point[i] > reference[i]:
                        reference[i] = point[i]
                else:
                    if point[i] < reference[i]:
                        reference[i] = point[i]
        for i, obj in enumerate(problem.objectives):
            if obj.to_minimize:
                reference[i] += 1
            else:
                reference[i] -= 1
        return reference


class MultiList:
    """A special data structure needed by FonsecaHyperVolume.

    It consists of several doubly linked lists that share common nodes. So,
    every node has multiple predecessors and successors, one in every list.
    """

    class Node:
        def __init__(self, count, value=None):
            self.value = value
            self.next = [None] * count
            self.prev = [None] * count
            self.ignore = 0
            self.area = [0.0] * count
            self.volume = [0.0] * count

        def __str__(self):
            return str(self.value)

    def __init__(self, count):
        """
        Build 'count' number of doubly linked lists.
        :param count: Number of doubly linked lists
        :return:
        """
        self.count = count
        self.sentinel = MultiList.Node(count)
        self.sentinel.next = [self.sentinel] * count
        self.sentinel.prev = [self.sentinel] * count

    def __str__(self):
        strings = []
        for i in xrange(self.count):
            current_list = []
            node = self.sentinel.next[i]
            while node != self.sentinel:
                current_list.append(str(node))
                node = node.next[i]
            strings.append(str(current_list))
        string_repr = ""
        for string in strings:
            string_repr += string + "\n"
        return string_repr

    def __len__(self):
        """
        Returns the number of lists that are included in this MultiList.
        """
        return self.count

    def size(self, index):
        """
        Returns the length of the i-th list.
        """
        length = 0
        sentinel = self.sentinel
        node = sentinel.next[index]
        while node != sentinel:
            length += 1
            node = node.next[index]
        return length

    def append(self, node, index):
        """
        Appends a node to the end of the list at the given index.
        :param node: Node to be appended
        :param index: Index of list to be appended into
        """
        penultimate = self.sentinel.prev[index]
        node.next[index] = self.sentinel
        node.prev[index] = penultimate
        self.sentinel.prev[index] = node
        penultimate.next[index] = node

    def extend(self, nodes, index):
        """
        Extend the list at the given index with nodes
        :param nodes: Nodes to be appended
        :param index: Index of list to be extended
        """
        sentinel = self.sentinel
        for node in nodes:
            penultimate = sentinel.prev[index]
            node.next[index] = sentinel
            node.prev[index] = penultimate
            sentinel.prev[index] = node
            penultimate.next[index] = node

    @staticmethod
    def remove(node, index, bounds):
        """
        Removes and returns node from all lists in [0, index]
        :param node: Node to be removed
        :param index: Index to be removed till
        :param bounds:
        :return: Removed node
        """
        for i in xrange(index):
            pred = node.prev[i]
            succ = node.next[i]
            pred.next[i] = succ
            succ.prev[i] = pred
            if bounds[i] > node.value[i]:
                bounds[i] = node.value[i]
        return node

    @staticmethod
    def reinsert(node, index, bounds):
        """
        Inserts 'node' at the position it had in all lists in [0, 'index'[
        before it was removed. This method assumes that the next and previous
        nodes of the node that is reinserted are in the list.
        :param node: Node to be reinserted
        :param index: Index to be reinserted at
        :param bounds:
        """
        for i in xrange(index):
            node.prev[i].next[i] = node
            node.next[i].prev[i] = node
            if bounds[i] > node.value[i]:
                bounds[i] = node.value[i]


class Stat(O):
    def __init__(self, problem, optimizer):
        """
        Initialize the statistic object
        :param problem: Instance of problem
        :param optimizer: Instance of optimizer
        :return:
        Stat object that contains
        - problem
        - generations: population for each generation
        - evals: total number of evaluations
        - runtime: total runtime of optimization
        - IGD: Inverse Generational Distance for each generation
        - spread: Spread for each generation
        - hyper_volume: Hyper-volume for each generation
        - problem_name: Name of the problem
        - decisions: Decisions of the problem
        - objectives: Objectives of the problem
        - optimizer: Instance of the optimizer
        - gen_evals: Evals each generation
        - solutions: Final set of solutions
        """
        O.__init__(self)
        self._problem = problem
        self.generations = None
        self.evals = 0
        self.runtime = None
        self.IGD = None
        self.spread = None
        self.hyper_volume = None
        self.problem_name = problem.name
        self.decisions = problem.decisions
        self.objectives = problem.objectives
        self._optimizer = optimizer
        self.solutions = None
        self.gen_evals = None

    def update(self, population, evals=0):
        if self.generations is None:
            self.generations = []
        clones = []
        for one in population:
            clones.append(one.clone())
        self.generations.append(clones)
        self.evals += evals

    def update_solutions(self):
        if self.solutions:
            return
        self.solutions = []
        if not self._optimizer.is_pareto:
            # Exception for methods like gale that does
            # not generate solutions on the pareto front.
            for generation in self.generations:
                self.solutions.extend(generation)
            self.solutions = self.solutions[-self._optimizer.settings.pop_size:]
        else:
            self.solutions = self.generations[-1]


class Algorithm(O):
    def __init__(self, name, problem):
        """
        Base class algorithm
        :param name: Name of the algorithm
        :param problem: Instance of the problem
        :return:
        """
        O.__init__(self)
        self.name = name
        self.problem = problem
        self.stat = Stat(problem, self)
        self.select = None
        self.evolve = None
        self.recombine = None
        self._reference = None
        self.is_pareto = True
        self.gen = 0

    @staticmethod
    def solution_range(obtained):
        """
        Calculate the range for each objective
        """
        predicts = [o.objectives for o in obtained]
        solutions = [[] for _ in range(len(predicts[0]))]
        for predict in predicts:
            for i in range(len(predict)):
                solutions[i].append(predict[i])
        for i, solution in enumerate(solutions):
            print("Objective :", i,
                  "   Max = ", max(solutions[i]),
                  "   Min = ", min(solutions[i]))

    def run(self):
        assert False


class MOEA_D(Algorithm):
    """
    Implements Zhang & Li's MOEAD algorithm
    """

    def __init__(self, problem, population=None, **settings):
        Algorithm.__init__(self, 'MOEA_D', problem)
        self.settings = default_settings().update(**settings)
        self.population = population
        self.ideal = [sys.maxint if obj.to_minimize else -sys.maxint for obj in self.problem.objectives]
        self.best_boundary_objectives = [None] * len(self.problem.objectives)
        self.distance = get_distance(self.settings.distance)
        self.crossover = get_crossover(self.settings.crossover)
        self.neighborhood = "local"

    def setup(self, population):
        """
        Mark each point with the nearest "T"
        weight vectors and return the global best.
        """
        self.init_weights(population)
        for key in population.keys():
            population[key].evaluate(self.problem, self.stat, 1)
        for one in population.keys():
            distances = []
            ids = []
            for two in population.keys():
                if one == two:
                    continue
                ids.append(two)
                distances.append(eucledian(population[one].weight, population[two].weight))
            sorted_ids = [index for dist, index in sorted(zip(distances, ids))]
            population[one].neighbor_ids = sorted_ids[:self.settings.T]
        for key in population.keys():
            self.update_ideal(population[key])

    def init_weights(self, population):
        """
        Initialize weights. We first check if we can generate
        uniform weights using the Das Dennis Technique.
        If not, we randomly generate them.
        :param population:
        """
        m = len(self.problem.objectives)

        def random_weights():
            wts = []
            for _, __ in population.items():
                wt = [random.random() for _ in xrange(m)]
                tot = sum(wt)
                wts.append([wt_i / tot for wt_i in wt])
            return wts

        divs = DIVISIONS.get(m, None)
        weights = None
        if divs:
            weights = cover(m, divs[0], divs[1])
        if weights is None or len(weights) != len(population):
            weights = random_weights()
        assert len(weights) == len(population), "Number of weights != Number of points"
        weights = shuffle(weights)
        for i, key in enumerate(population.keys()):
            population[key].weight = weights[i]

    def reproduce(self, point, population):
        child = self.crossover(self, point, population)
        child = poly_mutate(self.problem, child, eta=self.settings.nm)
        mutant = MOEADPoint(child)
        return mutant

    def run(self):
        # from measures.igd import igd
        start = get_time()
        # ideal_pf = self.problem.get_pareto_front()
        if self.population is None:
            self.population = self.problem.populate(self.settings.pop_size)
        population = {}
        for one in self.population:
            pt = MOEADPoint(one)
            population[pt.id] = pt
        self.setup(population)
        self.stat.update(population.values())
        while self.gen < self.settings.gens:
            print(".")
            self.gen += 1
            for point_id in shuffle(population.keys()):
                mutant = self.reproduce(population[point_id], population)
                mutant.evaluate(self.problem, self.stat, self.gen)
                self.update_ideal(mutant)
                self.update_neighbors(population[point_id], mutant, population)
            # objs = [population[pt_id].objectives for pt_id in population.keys()]
            self.stat.update(population.values())
        self.stat.runtime = get_time() - start
        return population

    def update_ideal(self, point):
        for i, obj in enumerate(self.problem.objectives):
            if obj.to_minimize:
                if point.objectives[i] < self.ideal[i]:
                    self.ideal[i] = point.objectives[i]
                    self.best_boundary_objectives[i] = point.objectives[:]
            else:
                if point.objectives[i] > self.ideal[i]:
                    self.ideal[i] = point.objectives[i]
                    self.best_boundary_objectives[i] = point.objectives[:]

    def update_neighbors(self, point, mutant, population):
        pdb.set_trace()
        ids = point.neighbor_ids if self.neighborhood == "local" else population.keys()
        for neighbor_id in ids:
            neighbor = population[neighbor_id]
            neighbor_distance = self.distance(self, neighbor.objectives, neighbor.weight)
            mutant_distance = self.distance(self, mutant.objectives, neighbor.weight)
            if mutant_distance < neighbor_distance:
                population[neighbor_id].decisions = mutant.decisions
                population[neighbor_id].objectives = mutant.objectives

    def get_nadir_point(self, population):
        nadir = [-sys.maxint if obj.to_minimize else sys.maxint for obj in self.problem.objectives]
        for point in population.values():
            for i, obj in enumerate(self.problem.objectives):
                if obj.to_minimize:
                    if point.objectives[i] > nadir[i]:
                        nadir[i] = point.objectives[i]
                else:
                    if point.objectives[i] < nadir[i]:
                        nadir[i] = point.objectives[i]
        return nadir


class Decision(O):
    def __init__(self, name, low, high):
        O.__init__(self)
        self.name = name
        self.low = low
        self.high = high

    def norm(self, val):
        return norm(val, self.low, self.high)

    def de_norm(self, val):
        return de_norm(val, self.low, self.high)

    def trim(self, val):
        return max(self.low, min(self.high, val))


class Objective(O):
    def __init__(self, name, to_minimize=True, low=None, high=None):
        O.__init__(self)
        self.name = name
        self.to_minimize = to_minimize
        self.low = low
        self.high = high
        self.value = None

    def norm(self, val):
        if self.low is None or self.high is None:
            return val
        else:
            return norm(val, self.low, self.high)


class Problem(O):
    def __init__(self):
        O.__init__(self)
        self.name = ""
        self.desc = ""
        self.decisions = []
        self.objectives = []
        self.evals = 0
        self.population = []
        self.ideal_decisions = None
        self.ideal_objectives = None
        self.constraints = []

    def title(self):
        return self.name + "_" + str(len(self.decisions)) + "_" + str(len(self.objectives))

    def generate(self, check_constraints=True):
        while True:
            one = [uniform(d.low, d.high) for d in self.decisions]
            if check_constraints:
                status = self.check_constraints(one)
                if status:
                    return one
            else:
                return one

    def assign(self, decisions):
        for i, d in enumerate(self.decisions):
            d.value = decisions[i]

    def directional_weights(self):
        """
        Method that returns an array of weights
        based on the objective. If objective is
        to be maximized, return 1 else return 0
        :return:
        """
        weights = []
        for obj in self.objectives:
            # w is negative when we are maximizing that objective
            if obj.to_minimize:
                weights.append(1)
            else:
                weights.append(-1)
        return weights

    def populate(self, n, check_constraints=True):
        """
        Default method to create a population
        :param n - Size of population
        """
        population = []
        for _ in range(n):
            population.append(self.generate(check_constraints))
        return population

    def norm(self, one, is_obj=True):
        """
        Method to normalize a point
        :param one - Point to be normalized
        :param is_obj - Boolean indicating Objective or Decision
        """
        normalized = []
        if is_obj:
            features = self.objectives
        else:
            features = self.decisions
        for i, feature in enumerate(one):
            normalized.append(features[i].norm(feature))
        return normalized

    def dist(self, one, two, one_norm=True, two_norm=True, is_obj=True):
        """
        Returns normalized euclidean distance between one and two
        :param one - Point A
        :param two - Point B
        :param one_norm - If A has to be normalized
        :param two_norm - If B has to be normalized
        :param is_obj - If the points are objectives or decisions
        """
        one_norm = self.norm(one, is_obj) if one_norm else one
        two_norm = self.norm(two, is_obj) if two_norm else two
        delta = 0
        count = 0
        for i, j in zip(one_norm, two_norm):
            delta += (i - j) ** 2
            count += 1
        return (delta / count) ** 0.5

    def manhattan_dist(self, one, two, one_norm=True, two_norm=True, is_obj=True):
        """
        Returns manhattan distance between one and two
        :param one - Point A
        :param two - Point B
        :param one_norm - If A has to be normalized
        :param two_norm - If B has to be normalized
        :param is_obj - If the points are objectives or decisions
        """
        one_norm = self.norm(one, is_obj) if one_norm else one
        two_norm = self.norm(two, is_obj) if two_norm else two
        delta = 0
        for i, j in zip(one_norm, two_norm):
            delta += abs(i - j)
        return delta

    def evaluate(self, decisions):
        pass

    def get_ideal_decisions(self, count=500):
        return None

    def get_ideal_objectives(self, count=500):
        return None

    def evaluate_constraints(self, decisions):
        return True, 0

    def check_constraints(self, decisions):
        return True

    def better(self, one, two):
        """
        Function that checks which of the
        two decisions are dominant
        :param one:
        :param two:
        :return:
        """
        obj1 = one.objectives
        obj2 = two.objectives
        one_at_least_once = False
        two_at_least_once = False
        for index, (a, b) in enumerate(zip(obj1, obj2)):
            status = compare(a, b, self.objectives[index].to_minimize)
            if status == -1:
                # obj2[i] better than obj1[i]
                two_at_least_once = True
            elif status == 1:
                # obj1[i] better than obj2[i]
                one_at_least_once = True
            if one_at_least_once and two_at_least_once:
                # neither dominates each other
                return 0
        if one_at_least_once:
            return 1
        elif two_at_least_once:
            return 2
        else:
            return 0

    def binary_dominates(self, one, two):
        """
        Check if one dominates two
        :param one: Point one
        :param two: Point two
        :return:
        1 if one dominates two
        2 if two dominates one
        0 if one and two are non-dominated
        """
        one_at_least_once = False
        two_at_least_once = False
        for index, (a, b) in enumerate(zip(one, two)):
            status = compare(a, b, self.objectives[index].to_minimize)
            if status == -1:
                # obj2[i] better than obj1[i]
                two_at_least_once = True
            elif status == 1:
                # obj1[i] better than obj2[i]
                one_at_least_once = True
            if one_at_least_once and two_at_least_once:
                # neither dominates each other
                return 0
        if one_at_least_once:
            return 1
        elif two_at_least_once:
            return 2
        else:
            return 0

    def get_pareto_front(self):
        """
        Get the pareto frontier
        for the problem from
        file in
        :return: List of lists of the pareto frontier
        """
        assert False


class DTLZ1(Problem):
    """
    Hypothetical test problem with
    "m" objectives and "n" decisions
    """
    k = 5

    def __init__(self, m, n=None):
        Problem.__init__(self)
        self.name = DTLZ1.__name__
        if n is None:
            n = DTLZ1.default_decision_count(m)
        self.decisions = [Decision("x" + str(index + 1), 0, 1) for index in range(n)]
        self.objectives = [Objective("f" + str(index + 1), True, 0, 1000) for index in range(m)]

    @staticmethod
    def default_decision_count(m):
        return m + DTLZ1.k - 1

    def evaluate(self, decisions):
        m = len(self.objectives)
        n = len(decisions)
        k = n - m + 1
        g = 0
        for i in range(n - k, n):
            g += ((decisions[i] - 0.5) ** 2 - cos(20.0 * PI * (decisions[i] - 0.5)))
        g = 100 * (k + g)
        f = []
        for i in range(0, m): f.append((1.0 + g) * 0.5)
        for i in xrange(m):
            for j in range(0, m - (i + 1)): f[i] *= decisions[j]
            if not (i == 0):
                aux = m - (i + 1)
                f[i] *= 1 - decisions[aux]
        return f


if __name__ == "__main__":
    o = DTLZ1(3)
    moead = MOEA_D(o, pop_size=91, gens=10)
    moead.run()

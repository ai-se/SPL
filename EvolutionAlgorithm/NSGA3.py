import math
import pdb
import sys
import numpy as np
from ecspy import ec
from ecspy import archivers
from ecspy import selectors
from copy import deepcopy
from random import shuffle, choice
from ecspy import replacers
from ecspy import terminators
from ecspy import variators

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"

"""
For transferring ecspy NSGA2 into NSGA3.
Special thanks to  george.ai-se
"""

EPS = 0.000001

DIVISIONS = {
  # Objectives : [outer_divs, inner_divs]
      3        : [        12,          0],
      4        : [         8,          0],  # TODO need double-check
      5        : [         6,          0],
      8        : [         3,          2],
      10       : [         3,          2],
      15       : [         2,          1]
}

def rand_one(lst):
  return choice(lst)

def splits(dim, div, outer=True):
  if outer:
    start = 0.0
    end = 1.0
  else:
    start = 1/(2*dim)
    end = start + 0.5
  delta = (end - start) / div
  return [start] + [start + i*delta for i in range(1, div)] + [end]


def expand(coords, possible):
  expanded  = []
  for coord in coords:
    for val in possible:
      new = coord + [val]
      if valid(new):
        expanded.append(new)
      else:
        break
  return expanded


def valid(coord, exact = False):
  if exact:
    return abs(sum(coord) - 1) < EPS
  else:
    return sum(coord) <= 1 + EPS


def reference(m, p, outer=True):
  """
  Create a set of reference points
  with m axes and p is the number of
  divisions along each axis
  :param m: Number of axis
  :param p: Number of divisions
  :return:
  """
  possible = splits(m, p, outer=outer)
  coords = [[pt] for pt in possible]
  for i in range(1, m):
    coords = expand(coords, possible)
  return [coord for coord in coords if valid(coord, exact=True)]


def cover(m, p_outer, p_inner=None):
  ref = reference(m, p_outer)
  if p_inner:
    ref += reference(m, p_inner, outer=False)
  return ref

class NSGAPoint(object):
    def __init__(self, ecs_i):
        self.ecs_i = ecs_i
        self.norm_objectives = deepcopy(ecs_i.fitness)
        self.perpendicular = None
        self.reference_id = None

class NSGA3(ec.EvolutionaryComputation):
    def __init__(self, random):
        ec.EvolutionaryComputation.__init__(self, random)
        self.archiver = archivers.best_archiver
        self.replacer = self.nsga3_replacement
        self.selector = selectors.tournament_selection
        self._reference = None
        self.objNum = 0
        self.pop_size = None

    def evolve(self, generator, evaluator, pop_size=100, seeds=[], maximize=True, bounder=ec.Bounder(), **args):
        args.setdefault('num_selected', pop_size)
        args.setdefault('tourn_size', 2)
        return ec.EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


    def nsga3_replacement(self, random, population, parents, offspring, args):
        """Replaces population using the non-dominated sorting technique from NSGA-II.

        .. Arguments:
           random -- the random number generator object
           population -- the population of individuals
           parents -- the list of parent individuals
           offspring -- the list of offspring individuals
           args -- a dictionary of keyword arguments

        """
        survivors = []
        combined = population[:]
        combined.extend(offspring[:])
        self.objNum = len(combined[0].fitness)
        self.pop_size = len(population)
        # Perform the non-dominated sorting to determine the fronts.
        fronts = []
        pop = set(range(len(combined)))
        while len(pop) > 0:
            front = []
            for p in pop:
                dominated = False
                for q in pop:
                    if combined[p] < combined[q]:
                        dominated = True
                        break
                if not dominated:
                    front.append(p)
            fronts.append([dict(individual=combined[f], index=f) for f in front])
            pop = pop - set(front)

        # Go through each front and add all the elements until doing so
        # would put you above the population limit. At that point, fall
        # back to the crowding distance to determine who to put into the
        # next population. Individuals with higher crowding distances
        # (i.e., more distance between neighbors) are preferred.
        for i, front in enumerate(fronts):
            if len(survivors) + len(front) > len(population):
                pop_next = []
                s = []
                front_individual = [f['individual'] for f in front]
                for i in survivors+front_individual:
                    s.append(NSGAPoint(i))
                references = self.get_references()
                self.associate(s, references)
                pop_next = self.niche(s, pop_next, references)
                survivors = [p.ecs_i for p in pop_next]
                return survivors
            else:
                for f in front:
                    if f['individual'] not in survivors:
                        survivors.append(f['individual'])
        return survivors

    def normalize(self, points):
        """
        Normalize set of points
        :param points:
        :return:
        """
        ideal = self.get_ideal(points)
        extremes = self.get_extremes(points, ideal)
        worst = self.get_worst(points)
        intercepts = self.get_intercepts(extremes, ideal, worst)
        for point in points:
            norm_objectives = []
            for i, o in enumerate(point.objectives):
                norm_objectives.append((o - ideal[i]) / (intercepts[i] - ideal[i] + 0.0000001))
            point.norm_objectives = norm_objectives
        return points

    @staticmethod
    def associate(population, references):
        """
        Associate a set of points to a set of
        reference vectors
        :param population: List of NSGAPoint
        :param references: List of reference vectors
        :return: population with each normalized vector
        associated with a reference vector
        """
        for point in population:
            min_dist = sys.maxint
            index = None
            for i, reference in enumerate(references):
                dist = NSGA3.perpendicular(point.norm_objectives, reference)
                if dist < min_dist:
                    min_dist = dist
                    index = i
            point.perpendicular = min_dist
            point.reference_id = index
        return population

    @staticmethod
    def perpendicular(vector, reference):
        """
        Perpendicular distance between a
        vector and its projection on a reference
        :param vector: Point to be projected. List of float
        :param reference: Reference to be projected on. List of float
        :return:
        """
        projection = 0
        reference_len = 0
        for v, r in zip(vector, reference):
            projection += v * r
            reference_len += r ** 2
        reference_len **= 0.5
        projection = abs(projection) / reference_len
        normal = 0
        for v, r in zip(vector, reference):
            normal += (v - projection * r / reference_len) ** 2
        return normal ** 0.5

    def niche(self, all_points, current_points, references):
        """
        Get Niche points for next generation from
        population
        :param all_points: Points to select from
        :param current_points: Population
        :param references: Reference points
        :return:
        """
        n = self.pop_size
        k = n - len(current_points)
        last_points = deepcopy(all_points[len(current_points):])
        ref_counts = [0] * len(references)
        ref_status = [False] * len(references)
        for point in current_points:
            ref_counts[point.reference_id] += 1

        index = 0
        while index < k:
            ref_ids = range(len(references))
            shuffle(ref_ids)
            least = sys.maxint
            ref_id = -1
            for ref_index in ref_ids:
                if not ref_status[ref_index] and ref_counts[ref_index] < least:
                    least = ref_counts[ref_index]
                    ref_id = ref_index
            feasibles = []
            for point in last_points:
                if point.reference_id == ref_id:
                    feasibles.append(point)
            if feasibles:
                best_point = 0
                if ref_counts[ref_id] == 0:
                    least_dist = sys.maxint
                    for point in feasibles:
                        if point.perpendicular < least_dist:
                            least_dist = point.perpendicular
                            best_point = point
                else:
                    best_point = rand_one(feasibles)
                current_points.append(best_point)
                ref_counts[ref_id] += 1
                last_points.remove(best_point)
                index += 1
            else:
                ref_status[ref_id] = True
        return current_points

    def get_references(self):
        """
        Get reference points for problems
        :return:
        """
        if self._reference is None:
            m = self.objNum
            divs = DIVISIONS[m]
            self._reference = cover(m, divs[0], divs[1])
        return self._reference

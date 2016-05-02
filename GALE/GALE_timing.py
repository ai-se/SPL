from time import time

from numpy import *

from problem import *


#from result_stat import Stat
#show = Stat.rdivDemo

# pdb.set_trace = lambda: None
class GALE(object):
    def __init__(self, model, np=100):
        self.model = model
        self.np = np  # initial population size

    ##################################################
    # Canx  : candidate 1                            #
    # cany  : candidate 2                            #
    # return: distance of decs between candidate 1&2 #
    ##################################################
    def dist(self, canx, cany):
        x, y = canx.decs, cany.decs
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(x, y))) / math.sqrt(len(x))

    ##################################
    # x     : given candidate        #
    # data  : candidate list         #
    # return: the furthest candidate #
    ##################################
    def furthest(self, x, data):
        dis, p = 0, x
        for a in data:
            temp = self.dist(x, a)
            if temp > dis:
                dis, p = temp, a
        return p

    #########################################
    # data  : given candidate list          #
    # return: the left part, the right part #
    #########################################
    def split(self, data):
        mid = len(data) / 2
        return data[:mid], data[mid:]

    ##########################################
    # west  : west candidate                 #
    # east  : east candidate                 #
    # c     : distance between west and east #
    # return: projected DIST in west~east    #
    ##########################################
    def project(self, west, east, c, x):
        a = self.dist(x, west)
        b = self.dist(x, east)
        return (a ** 2 + c ** 2 - b ** 2) / (2 * c)  # cosin rule

    ######################################
    # data  : given candidate list       #
    # return: west pole, east pole, dist #
    ######################################
    def getPoles(self, data):
        z = random.choice(data)
        west = self.furthest(z, data)
        east = self.furthest(west, data)
        c = self.dist(west, east)
        return west, east, c

    #############################################################
    # data  : given candidate list                              #
    # return: west pole, east pole, dist, LEFT part, RIGHT part #
    #############################################################
    def fastmap(self, data):
        west, east, c = self.getPoles(data)
        if c != 0:
            data.sort(key=lambda x: self.project(west, east, c, x))
        LEFT, RIGHT = self.split(data)
        return west, east, c, LEFT, RIGHT

    ####################################################
    # WARNING scores should have filled in the x and y #
    # better indicates MUCH BETTER!                    #
    # canx  : first candidate                          #
    # cany  : first candidate                          #
    # return: true is x better than y; otherwise false #
    ####################################################
    def better(self, canx, cany):
        """"
        def loss(x, y):
            sum = 0
            for t in range(self.model.objNum):
                if self.model.obj[t].goal == lt:
                    sum += -1 * math.exp((x.scores[t] - y.scores[t]) / self.model.objNum)
                else:
                    sum += -1 * math.exp((y.scores[t] - x.scores[t]) / self.model.objNum)
            return sum / self.model.objNum

        if x == y: return False
        return loss(canx, cany) > loss(cany, canx)
        """
        index = 0
        for x, y, m in zip(canx.fitness, cany.fitness, self.model.obj):
            index += (x-y)/(m.hi-m.lo)
        #print index
        return index > 0.15

    ##############################################################################################
    # data  : candidates tried to decomposs                                                      #
    # lvl   : recursion level                                                                    #
    # prune : whether to prune (basing on the the score in the poles)                            #
    # return: representive scores(deepest poles scores) and the leafs set(each set is a cluster) #
    ##############################################################################################
    def where(self, data, lvl=100, prune=True):
        omega = math.sqrt(self.np)
        west, east, c, left, right = self.fastmap(data)
        self.model.eval(west)
        self.model.eval(east)
        goWest = len(left) > omega
        goEast = len(right) > omega
        if lvl < 1 or (not (goWest and goEast)):
            return [west.fitness, east.fitness], data
        if prune:
            if goEast and self.better(west, east): goEast = False
            if goWest and self.better(east, west): goWest = False
        leafs = []
        fitness = []
        #if goWest and goEast: print "not comparable for data size = ", len(data)
        if goWest:
            sw, lw = self.where(left, lvl - 1, prune)
            fitness.extend(sw)
            ll = [x for x in item(lw)]
            leafs.append(ll)
        if goEast:
            sr, lr = self.where(right, lvl - 1, prune)
            fitness.extend(sr)
            rr = [x for x in item(lr)]
            leafs.append(rr)
        return fitness, leafs

    ###############################################
    # Nudge the old towards east, but not too far #
    # East is better than the west                #
    # ~~~                                         #
    # old    : the candidate tried to nudge       #
    # c      : distance between east and west     #
    # east   : east pole candidate                #
    # west   : west pole candidate                #
    # gamma  : radidus rate thresold              #
    # delta  : nudge force setting                #
    # return : the new candiate                   #
    ###############################################
    def mutate1(self, old, c, east, west, gamma=1.5, delta=1.3):
        if c == 0: return old
        new = o(decs=old.decs[:], fitness=[])  # copy the decisions and omit the score
        index = 0
        for n, e, w, H in zip(new.decs, east.decs, west.decs, self.model.dec):
            d = sign(e - n)
            # n = delta * n * (1 +abs(c)*d)
            n = n + d * (abs(e - n) * delta)
            new.decs[index] = H.restrain(n)  # avoid running out of the range
            index += 1
        newDist = self.project(west, east, c, new) - \
                  self.project(west, east, c, west)
        if abs(newDist) < gamma * abs(c) :#and self.model.ok(new):
            return new
        return old

    #####################################
    # mutate the leafs by mutate1 above #
    #####################################
    def mutate(self, leafs):
        out = []
        for leaf in leafs:
            r = []
            west, east, c = self.getPoles(leaf)
            if west.fitness == []: self.model.eval(west)
            if east.fitness == []: self.model.eval(east)
            if self.better(west, east): east, west = west, east
            for candidate in leaf:
                r.append(self.mutate1(candidate, c, east, west))
            out.append(r)
        return out

    def tool_print_pop_dist(self, cans, noprint=False):
        N = len(cans)
        result = []
        for i, f in enumerate(self.model.ft.leaves):
            s = sum(c.decs[i] for c in cans)
            p = round(s / (N + 0.0001), 2)
            result.append(p)
        if not noprint: print result
        return result

    ###################################
    # the kernel of the gale function #
    ###################################
    def gale(self, enough=16, max=1000, lamb=50):
        """
        old : scores sets to be evaluated
        new : scores sets to be evaluated
        return whether new is improved.(as long as one obj is imporved, return True)
        """

        def improved(old, new):
            for q in range(self.model.objNum):
                before = mean([p[q] for p in old])
                now = mean([p[q] for p in new])
                if self.model.obj[q].goal(now, before): return True
            return False

        t = time()
        pop = [self.model.genRandomCan() for _ in range(self.np)]
        self.time_ran_pop += time()-t
        #e = self.tool_print_pop_dist(pop)
        patience = lamb
        for generation in range(max):
            #print '-'*30, generation
            fitness = []
            t = time()
            fitness, leafs = self.where(pop)
            self.time_where += time()-t
            #print len(leafs),
            t = time()
            mutants = self.mutate(leafs)
            valid = 0
            invalid = 0
            for i2 in mutants[0]:
                if self.model.ok(i2):
                    valid+=1
                else:
                    invalid += 1
            print float(valid)/(valid+invalid)
            self.time_mutate += time()-t
            if generation > 0:
                if not improved(oldScores, fitness):
                    patience -= 1
                if patience < 0 or generation == max - 1:
                    _, leafs = self.where(pop, prune=True)
                    r = []
                    for x in item(leafs):
                        r.append(x)
                    return r
            oldScores = fitness
            pop = []
            for m in item(mutants): pop.append(m)
            required = self.np - len(pop)
            t = time()
            for _ in range(required): pop.append(self.model.genRandomCan())
            self.time_ran_pop += time()-t

def testw_baseline():
    k_model = ZDT2()
    k_model.learn_base_line(1000)
    g = GALE(k_model)
    v = g.gale(lamb=10000)
    pdb.set_trace()


if __name__ == '__main__':
    testw_baseline()

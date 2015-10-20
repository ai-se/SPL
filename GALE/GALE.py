import math, random
from numpy import *
from ZDT4 import *
from model import *
from problem import *
from o import *

#pdb.set_trace = lambda: None
class GALE(object):
    def __init__(self, model, np=100):
        self.model = model
        self.np = np # initial population size


    ##################################################
    # Canx  : candidate 1                            #
    # cany  : candidate 2                            #
    # return: distance of decs between candidate 1&2 #
    ##################################################
    def dist(self, canx, cany):
        x,y = canx.decs, cany.decs
        return math.sqrt(sum( (a - b)**2 for a, b in zip(x, y))) / math.sqrt(len(x))


    ##################################
    # x     : given candidate        #
    # data  : candidate list         #
    # return: the furthest candidate #
    ##################################
    def furthest(self, x, data):
        dis, p = 0,x
        for a in data:
            temp = self.dist(x,a)
            if temp > dis:
                dis, p = temp, a
        return p


    #########################################
    # data  : given candidate list          #
    # return: the left part, the right part #
    #########################################
    def split(self, data):
        mid = len(data)/2
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
        return (a**2 + c**2 - b**2) / (2*c) # cosin rule

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
            data.sort(key = lambda x: self.project(west,east,c,x))
        LEFT,RIGHT = self.split(data)
        return west, east, c, LEFT, RIGHT


    ####################################################
    # WARNING scores should have filled in the x and y #
    # x     : first candidate                          #
    # y     : first candidate                          #
    # return: true is x better than y; otherwise false #
    ####################################################
    def better(self, x, y):
        def loss(x,y):
            sum = 0
            for t in range(self.model.objNum):
                if self.model.obj[t].goal == lt:
                    sum += -1 * math.exp((x.scores[t]-y.scores[t])/self.model.objNum)
                else:
                    sum += -1 * math.exp((y.scores[t]-x.scores[t])/self.model.objNum)
            return sum / self.model.objNum
        if x == y : return False
        return loss(x,y) > loss(y,x)


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
        goWest = len(left)  > omega
        goEast = len(right) > omega
        if lvl < 1 or (not (goWest and goEast)):
            #return [self.center(data).scores], data  #IDEA: using center instead of poles
            return [west.scores, east.scores], data
        if prune:
            if goEast and self.better(west, east): goEast = False
            if goWest and self.better(east, west): goWest = False
        leafs = []
        scores = []
        if goWest:
            sw,lw = self.where(left, lvl-1, prune)
            scores.extend(sw)
            ll = [x for x in item(lw)]
            leafs.append(ll)
        if goEast:
            sr, lr = self.where(right, lvl-1, prune)
            scores.extend(sr)
            rr = [x for x in item(lr)]
            leafs.append(rr)
        return scores, leafs


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
    def mutate1(self, old, c, east, west, gamma=1.5, delta=0.5):
        if c == 0: return old
        new = o(decs=old.decs[:],scores=[]) #copy the decisions and omit the score
        index = 0
        for n,e,w,H in zip(new.decs, east.decs, west.decs, self.model.dec):
            d = sign(e - n)
            #n = delta * n * (1 +abs(c)*d)
            n = n + d * (abs(e-n) * delta)
            new.decs[index] = H.restrain(n) # avoid running out of the range
            index += 1
        newDist = self.project(west, east, c, new) - \
                  self.project(west, east, c, west)
        if abs(newDist) < gamma * abs(c) and self.model.ok(new):
            return new
        return old


    #####################################
    # mutate the leafs by mutate1 above #
    #####################################
    def mutate(self, leafs):
        out = []
        #pdb.set_trace()
        for leaf in leafs:
            r = []
            west, east, c = self.getPoles(leaf)
            if west.scores == []: self.model.eval(west)
            if east.scores == []: self.model.eval(east)
            if self.better(west, east): east, west = west, east
            for candidate in leaf:
                r.append(self.mutate1(candidate,c,east,west))
            out.append(r)
        return out


    ###################################
    # the kernel of the gale function #
    ###################################
    def gale(self, enough=16, max=1000, lamb=50):
        """
        old : scores sets to be evaluated
        new : scores sets to be evaluated
        return whether new is improved.(as long as one obj is imporved, return True)
        """
        def improved(old,new):
            for q in range(self.model.objNum):
                before = mean([p[q] for p in old])
                now    = mean([p[q] for p in new])
                if self.model.obj[q].goal(now, before): return True
            return False

        pop = [self.model.genRandomCan() for _ in range(self.np)]
        #print 'initial pop','-'*10
        #print sort([round(a.decs[0],0) for a in pop])
        #pdb.set_trace()
        patience = lamb
        for generation in range(max):
            print '-'*30, generation
            scores = []
            scores, leafs = self.where(pop)
            """
            print 'before mutation'
            for x in item(leafs):
                print round(x.decs[0],2),
            print
            """
            mutants = self.mutate(leafs)
            """
            print 'after mutation'
            for x in item(mutants):
                print round(x.decs[0],2),
            print
            """
            if generation > 0:
                if not improved(oldScores, scores):
                    patience -= 1
                if patience < 0:
                    _, leafs = self.where(pop, prune = True)
                    r = []
                    for x in item(leafs):
                        r.append(x)
                    return r
            oldScores = scores
            pop=[]
            for m in item(mutants): pop.append(m)
            required = self.np - len(pop)
            for _ in range(required): pop.append(self.model.genRandomCan())
            """
            print 'pop for next generation'
            for x in pop:
                print round(x.decs[0],2),
            print
            """
            #pdb.set_trace()


def testw_baseline():
    k_model = Schaffer()
    k_model.learn_base_line(1000)
    g = GALE(k_model)
    v = g.gale()
    pdb.set_trace()

if __name__ == '__main__':
    testw_baseline()


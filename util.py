from collections import deque
from itertools import count
import copy
import math
import random

class Constraint(object):
    """
    Constrains a single object of class Variable. (see p. 84 of Ovans)

    """
    def __repr__(self):
        return 'Constraint object with var {}'.format(self.var)

    def setVariable(self, var):
        self.var = var

class Constraint3(Constraint):
    def __repr__(self):
        return 'Constraint3 object with var {}, var2 {}'.format(self.var, self.var2)

    def setVariable2(self, var):
        self.var2 = var

class Link(object):
    def __init__(self):
        # See p. 32 in Ovans
        self.label = None # selector for method restricting domains
        self.node = None # the constraint object we are incident to

    def getLabel(self):
        return self.label

    def setNode(self, node):
        self.node = node

    def getNode(self):
        return self.node

    def setLabel(self, label):
        self.label = label

class Variable(object):
    _ids = count(0)

    def __init__(self, name):
        self.domain = [] # a list of objects. length 0 -> unsatisfiable
        self.neighbors = [] # collection of links
        self.name = name
        self.id = next(self._ids)

    def addToDomain(self, obj):
        self.domain.append(obj)

    def __repr__(self):
        return '<Variable name: {} domain: {}'.format(self.name, self.printDomain())

    def printDomain(self):
        return ''.join(map(lambda x: x.__repr__(), self.domain))

    def getDomain(self):
        return self.domain

    def setDomain(self, new):
        self.domain = new

    def addToNeighbors(self, link):
        self.neighbors.append(link)

class Csp(object):
    def __init__(self):
        self.vars = []
        self.bts = self.nodes = self.sol = self.iters = 0
        self.one_sol = None
        self.initial_domains = {}
        self.var_index = {}

    def addToVariables(self, var):
        self.vars.append(var)
        self.var_index[var.id] = var

    def getSol(self):
        return self.sol

    def getBts(self):
        return self.bts

    def getNodes(self):
        return self.nodes

    # See p. 209 of AIAMA for AC-3 pseudocode
    def createArcQueue(self):
        out = deque([]) # out should be a queue of arcs (var_1, var_2, constraint)
        for var in self.vars:
            for neighbor in var.neighbors:
                out.append((var, neighbor.node.var, neighbor.label))
        #print(out)
        return out

    def AC3(self):
        saved_vars = {}
        for j in range(len(self.vars)):
            saved_vars[j] = copy.deepcopy(self.vars[j].getDomain())

        queue = self.createArcQueue()

        success = True
        while len(queue) > 0:
            (x_i, x_j, constraint) = queue.popleft()
            if self.revise(x_i, x_j, constraint):
                if len(x_i.domain) == 0:
                    success = False
                    break
                for link in x_i.neighbors:
                    if link.node.var != x_j:
                        queue.append((x_i, link.node.var, link.label))

        if not success:
            for j in range(len(self.vars)):
                self.vars[j].setDomain(saved_vars[j])

        return success

    def revise(self, x_i, x_j, constraint):
        revised = False
        for val in x_i.domain:
            satisfied = False
            for val2 in x_j.domain:
                if constraint(val, val2):
                    satisfied = True
                    break
            if not satisfied:
                x_i.domain.remove(val)
                revised=True
        return revised

    def backtracking_search(self):
        return self.backtrack()

    def selectUnassignedVariable(self):
        # assume assignment is a set containing indices of assigned vars
        for var in self.vars:
            if len(var.domain) > 1:
                return var
        return None

    def orderDomainValues(self, var):
        return var.getDomain()

    def backtrack(self):
        saved_vars = {}
        for j in range(len(self.vars)): # save variables to restore them later
            saved_vars[j] = copy.deepcopy(self.vars[j].getDomain())

        cur_var = self.selectUnassignedVariable()
        if cur_var is None:
            # all variables are assigned, return
            # print 'cur_var is None with vars {}'.format(self.vars)
            self.one_sol = copy.deepcopy(self.vars)
            self.sol += 1
            return True

        for val in self.orderDomainValues(cur_var):
            cur_var.setDomain([val])
            self.nodes += 1
            if self.checkConsistent():
                inferences = self.AC3()
                if inferences:
                    result = self.backtrack()
                    if result != False:
                        return result
            self.bts += 1 # if we reach this point, we are backtracking

            for j in range(len(self.vars)): # restore variable domains
                self.vars[j].setDomain(saved_vars[j])

        return False

    def checkConsistent(self):
        # assume assignment is a set containing indices of assigned vars
        for var in self.vars:
            for link in var.neighbors:
                consistent = False
                for val in var.domain:
                    for val2 in link.node.var.domain:
                        if link.label(val, val2):
                            consistent=True
                            break
                    if consistent:
                        break
                if not consistent:
                    return False
        return True

    def getCost(self, vars): # Should return a cost heuristic representing distance from a satisfying assignment
        cost = 0
        for var in vars:
            member1 = var.getDomain()[0]
            for n in var.neighbors:
                constraint = n.getNode()
                member2 = constraint.var.getDomain()[0]
                try: # look for 3 constraints
                    member3 = constraint.var2.getDomain()[0]
                    if not n.label(member1, member2, member3):
                        cost += 1
                except AttributeError:
                    if not n.label(member1, member2):
                        cost += 1
        return cost

    def getNeighbor(self, vars):
        to_change = random.choice(range(len(vars)))
        new_val = random.choice(self.initial_domains[to_change])
        vars[to_change].setDomain([new_val])

    def simAnnealing(self):
        # generate random initialization
        T = 5000
        for i in range(len(self.vars)):
            self.initial_domains[i] = copy.deepcopy(self.vars[i].getDomain())
            self.vars[i].setDomain([random.choice(self.initial_domains[i])])
        cur_cost = self.getCost(self.vars)
        while self.getCost(self.vars) != 0 and T > 1:
            T -= 1
            self.iters += 1
            # save current assignments
            saved_vars = {}
            for i in range(len(self.vars)):
                saved_vars[i] = copy.deepcopy(self.vars[i].getDomain())

            new_assignment = self.getNeighbor(self.vars)

            # From https://en.wikipedia.org/wiki/Simulated_annealing#Acceptance_probabilities
            accept_prob = math.exp(-(float(self.getCost(self.vars))-float(cur_cost)/float(T)))
            if self.getCost(self.vars) > cur_cost and random.random() > accept_prob:
                for i in range(len(self.vars)):
                    self.vars[i].setDomain(saved_vars[i])
                continue
            else:
                cur_cost = self.getCost(self.vars)

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

    def revise(self, var_i, predicate):
        """
        revise(), defined on page 84 of Ovans 1990
        """
        domain1 = self.var.getDomain()
        domain2 = var_i.getDomain()
        newDomain = []
        changed = False

        for x in domain1:
            satisfied = False
            for y in domain2:
                if predicate(y, x):
                    satisfied = True
                    break
            if not satisfied:
                changed = True
            else:
                newDomain.append(x)
        if len(newDomain) == 0:
            return False
        elif changed:
            self.var.setDomain(newDomain)
            if self.var.alertChanged():
                return True
            else:
                self.var.setDomain(domain1)
                return False
        else:
            return True

class Constraint3(Constraint):
    def __repr__(self):
        return 'Constraint3 object with var {}, var2 {}'.format(self.var, self.var2)

    def setVariable2(self, var):
        self.var2 = var

    def revise(self, sender, constraint):
        domain1 = sender.getDomain()
        domain2 = self.var.getDomain()
        domain3 = self.var2.getDomain()
        newDomain2 = []
        newDomain3 = []
        changed = False

        # if len(domain2) == 0 or len(domain3) == 0 or len(domain1) == 0:
        #     return False

        # check that each member of domain 2 is satisfied
        # by at least one member of domain3 and domain1
        # if so, add it to the newDomain2
        #def domain_check(domain2, domain3, newDomain2, newDomain3):
        for memberD2 in domain2:
            satisfied = False
            for memberD3 in domain3:
                for memberD1 in domain1:
                    if constraint(memberD1, memberD2, memberD3):
                        satisfied = True
                    if satisfied:
                        break
                if satisfied:
                    break
            if not satisfied:
                changed = True
            else:
                newDomain2.append(memberD2)
                    #return False

        #changed = changed or domain_check(domain2, domain3, newDomain2, newDomain3)

        if len(newDomain2) == 0:
            return False

        #changed = changed or domain_check(domain3, domain2, newDomain3, newDomain2)

        for memberD3 in domain3:
            satisfied = False
            for memberD2 in domain2:
                for memberD1 in domain1:
                    if constraint(memberD1, memberD2, memberD3):
                        satisfied = True
                    if satisfied:
                        break
                if satisfied:
                    break
            if not satisfied:
                changed = True
            else:
                newDomain3.append(memberD3)

        if len(newDomain3) == 0:
            return False

        if changed:
            self.var.setDomain(newDomain2)
            self.var2.setDomain(newDomain3)
            if self.var.alertChanged() and self.var2.alertChanged():# propagate!
                return True
            else:
                self.var.setDomain(domain2)
                self.var2.setDomain(domain3)
                return False

        return True


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

    # notify all its neighbors that its domain has been changed
    # return True if the changes did not result in an empty set
    def alertChanged(self):
        i = 0
        result = True
        while (result and i < len(self.neighbors)):
            link = self.neighbors[i]
            result = link.getNode().revise(self, link.label)
            i += 1
        return result

    def instantiate(self, obj):
        # Test whether a given instantiation will work
        temp_domain = copy.deepcopy(self.domain)
        self.domain = [obj]
        if self.alertChanged():
            return True
        else:
            self.domain = temp_domain
            return False

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

    def findSolutions2(self, index, numVariables):
        if index == numVariables:
            self.sol += 1
            if self.sol == 10:
                self.one_sol = copy.deepcopy(self.vars)
            print('solution is {}'.format(self.vars))
            return

        cur_var = self.vars[index]
        cur_domain = copy.deepcopy(cur_var.getDomain())
        index += 1
        success = False
        for i in range(len(cur_domain)):
            saved_vars = {}
            for j in range(index, numVariables):
                saved_vars[j] = copy.deepcopy(self.vars[j].getDomain())
            if cur_var.instantiate(cur_domain[i]):
                success = True
                self.nodes += 1
                self.findSolutions2(index, numVariables)
            for j in range(index, numVariables):
                self.vars[j].setDomain(saved_vars[j])
        if not success:
            self.bts += 1

        cur_var.setDomain(cur_domain)

    def findSolutions(self):
        return self.findSolutions2(0, len(self.vars))

    def findOneSolution(self, index, numVariables):
        if index == numVariables:
            self.sol += 1
            self.one_sol = copy.deepcopy(self.vars)
            return True

        # select a variable from list to instantiate
        cur_var = self.vars[index]
        cur_domain = copy.deepcopy(cur_var.getDomain())
        index += 1

        # now try to instantiate the variable
        success = False
        for i in range(len(cur_domain)):
            saved_vars = {}
            for j in range(index, numVariables):
                saved_vars[j] = copy.deepcopy(self.vars[j].getDomain())
            if cur_var.instantiate(cur_domain[i]):
                self.nodes += 1
                success = self.findOneSolution(index, numVariables)

            #if not success:
            for j in range(index, numVariables):
                self.vars[j].setDomain(saved_vars[j])
            if success:
                break

        cur_var.setDomain(cur_domain)

        if not success:
            self.bts += 1
            return False
        else:
            return True

    def findASolution(self):
        return self.findOneSolution(0, len(self.vars))

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

        # to_check = list(range(len(self.vars)))
        # for id in to_check:
        #     for neighbor in self.vars[id].neighbors:
        #         for val in self.vars[id].domain:
        #             satisfied = False
        #             for val2 in neighbor.node.var:
        #                 if neighbor.label(val, val2):
        #                     satisfied=True
        #                     break
        #             if not satisfied:
        #                 self.vars[i].domain.remove(val)

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



    def makeArcConsistent(self):
        for i in range(len(self.vars)):
            if not self.vars[i].alertChanged(): # if a variable's domain is now empty
                print('failing variable is {}'.format(self.vars[i]))
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

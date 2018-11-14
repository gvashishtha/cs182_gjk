import copy

class Constraint(object):
    """
    Constrains a single object of class Variable. (see p. 25 of Ovans)

    """

    def setVariable(self, var):
        self.var = var

    def revise(self, var_i, predicate):
        """
        revise(), defined on page 10 of Ovans 1990
        """
        print('revise called with var_i {}, predicate {}'.format(var_i.name, predicate))
        domain1 = self.var.getDomain()
        domain2 = var_i.getDomain()
        newDomain = []
        changed = False

        for x in domain1:
            satisfied = False
            for y in domain2:
                if predicate(x, y):
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
    def setVariable2(self, var):
        self.var2 = var

    def revise(self, sender, constraint):
        domain1 = sender.getDomain()
        domain2 = self.var.getDomain()
        domain3 = self.var2.getDomain()
        newDomain2 = []
        newDomain3 = []
        changed = False

        # check that each member of domain 2 is satisfied
        # by at least one member of domain3 and domain1
        # if so, add it to the newDomain2
        def domain_check(domain2, domain3, newDomain2, newDomain3):
            for i in range(len(domain2)):
                memberD2 = domain2[i]
                satisfied = False

                j = 0
                while True:
                    memberD3 = domain3[j]
                    k = 0
                    while True:
                        if constraint(domain1[k], memberD2, memberD3):
                            satisfied = True
                        if satisfied or k >= len(domain1):
                            break
                    if satisfied or j >= len(domain3):
                        break

                if not satisfied:
                    return True

                else:
                    newDomain2.append(memberD2)
                    return False

        changed = changed or domain_check(domain2, domain3, newDomain2, newDomain3)

        if len(newDomain2) == 0:
            return False

        changed = changed or domain_check(domain3, domain2, newDomain3, newDomain2)

        if len(newDomain3) == 0:
            return False

        if changed:
            self.var.setDomain(newDomain2)
            self.var2.setDomain(newDomain3)
            if self.var.alertChanged() and self.var2.alertChanged():# propagate!
                return False
            else:
                self.var.setDomain(domain2)
                self.var.setDomain(domain3)
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
    def __init__(self, name):
        self.domain = [] # a list of objects. length 0 -> unsatisfiable
        self.neighbors = [] # collection of links
        self.name = name

    def addToDomain(self, obj):
        self.domain.append(obj)

    def __repr__(self):
        return '<Variable name: {}'.format(self.name)

    def printdomain(self):
        return (map(lambda x: x.__repr__(), self.domain).join())

    def getDomain(self):
        return self.domain

    def setDomain(self, new):
        self.domain = new

    def addToNeighbors(self, link):
        self.neighbors.append(link)

    # notify all its neighbors that its domain has been changed
    # return True if the changes did not result in an empty set
    def alertChanged(self):
        #print('alert changed called on {} with neighbors{}'.format(self.name, self.neighbors))
        i = 0
        result = True
        while (result and i < len(self.neighbors)):
            link = self.neighbors[i]
            result = link.getNode().revise(self, link.label)
            i += 1
        return result

    def instantiate(self, domain):
        new_var = Variable(self.name + 'child')
        if new_var.alertChanged():
            return True
        else:
            return False

class Csp(object):
    def __init__(self):
        self.vars = []
        self.bts = self.nodes = self.sol = 0

    def addToVariables(self, var):
        self.vars.append(var)

    def findSolutions2(self, index, numVariables):
        if index == numVariables:
            self.sol += 1
            map(lambda x: x.printDomain(), self.vars)
            return

        cur_var = self.vars[index]
        cur_domain = copy.deepcopy(cur_var.getDomain())
        index += 1

        success = False
        for i in range(len(cur_domain)):
            saved_vars = []
            for j in range(index, numVariables):
                saved_vars.append(copy.deepcopy(self.vars[j]))
                if cur_var.instantiate(cur_domain[i]):
                    success = True
                    self.nodes += 1
                    self.findSolutions2(index, numVariables)
            for j in range(index, numVariables):
                self.vars[j] = saved_vars[j]
        if not success:
            self.bts += 1

        cur_var.setDomain(cur_domain)

    def findSolutions(self):
        return self.findSolutions2(0, len(self.vars))

    def findOneSolution(self, index, numVariables):
        if index == numVariables:
            self.sol += 1
            map(lambda x: x.printDomain(), self.vars)
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
                saved_vars[j] = (copy.deepcopy(self.vars[j]))
                if cur_var.instantiate(cur_domain[i]):
                    self.nodes += 1
                    success = self.findOneSolution(index, numVariables)
            for j in range(index, numVariables):
                try:
                    self.vars[j] = saved_vars[j]
                except IndexError:
                    print('Index Error: j is {}, index is {}, self.vars is {}, saved_vars is {}'.format(j, index, self.vars, saved_vars))
            if success:
                break

        cur_var.setDomain(cur_domain)

        if not success:
            self.bts += 1
            return False

    def findASolution(self):
        return self.findOneSolution(0, len(self.vars))

    def getSol(self):
        return sol

    def getBts(self):
        return bts

    def getNodes(self):
        return nodes

    def makeArcConsistent(self):
        for i in range(len(self.vars)):
            if not self.vars[i].alertChanged(): # if a variable's domain is now empty
                return False
        return True

import copy

class Constraint(object):
    """
    Constrains a single object of class Variable. (see p. 25 of Ovans)

    """
    def __init__(self, var):
        self.var = var

    def setVariable(self, var):
        self.var = var

    def revise(self, var_i, predicate):
        """
        revise(), defined on page 10 of Ovans 1990
        """
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
    def __init__(self, name, domain):
        self.domain = [] # a list of objects. length 0 -> unsatisfiable
        self.neighbors = [] # collection of links
        self.name = name

    def addToDomain(self, obj):
        self.domain.append(obj)

    def __repr__(self):
        print '<Variable name: {}'.format(self.name)

    def printdomain(self):
        map(lambda x: print(x), self.domain)

    def getDomain(self):
        return self.domain

    def setDomain(self, new):
        self.domain = new

    def addToNeighbors(self, link):
        self.neighbors.append(link)

    def alertChanged(self):
        i = 0
        result = True
        while (result and i < len(self.neighbors)):
            link = self.neighbors[i]
            result = link.getNode().revise(self.domain, link.label)
            i += 1
        return result

    def instantiate(self, domain):
        new_var = Variable(None, domain)
        if new_var.alertChanged():
            return True
        else:
            return False

class Csp(object):
    def __init__(self, var_list):
        self.vars = var_list
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

        

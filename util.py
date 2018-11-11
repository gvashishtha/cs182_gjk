def revise(var_i, var_j, predicate):
    """
    revise(), defined on page 10 of Ovans 1990
    """
    change = False
    for x in var_i.domain:
        check = False
        for y in var_j.domain:
            if predicate(x, y):
                check = True
                break
        if check:
            var_i.domain.remove(var)
            change = True
    return change




class Constraint(object):
    def setVariable(self, var):
        self.var = var

class Link(object):
    def __init__(self):
        self.label = None
        self.node = None

    def getLabel(self):
        return self.label

    def setNode(self, node):
        self.node = node

    def getNode(self):
        return self.node

    def setLabel(self, label):
        self.label = label

class Variable(object):
    def __init__(self):
        self.domain = []
        self.neighbors = []

    def addToDomain(self, obj):
        self.domain.append(obj)

    def addToNeighbors(self, link):
        self.neighbors.append(link)

    def alertChanged(self):
        i = 0
        result = True
        while (result and i < len(self.neighbors)):
            link = self.neighbors[i]
            result = revise(link.getNode())
            i += 1

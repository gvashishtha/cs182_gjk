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
        #print('revise called with var_i {}, predicate {}'.format(var_i.name, predicate))
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
    def __init__(self, name):
        self.domain = [] # a list of objects. length 0 -> unsatisfiable
        self.neighbors = [] # collection of links
        self.name = name

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
        #print('alert changed called on {} with neighbors{}'.format(self.name, self.neighbors))
        i = 0
        result = True
        while (result and i < len(self.neighbors)):
            link = self.neighbors[i]
            result = link.getNode().revise(self, link.label)
            #if not result:
                #print('we are {}. \n\nfailed test at {} \n\nand {}'.format(self.__repr__(), link.node.var,link.node.var2))
            i += 1
        return result

    def instantiate(self, obj):
        #new_var = Variable(self.name + 'child')
        temp_domain = copy.deepcopy(self.domain)
        self.domain = [obj]
        if  self.alertChanged():
            return True
        else:
            self.domain = temp_domain
            return False

class Csp(object):
    def __init__(self):
        self.vars = []
        self.bts = self.nodes = self.sol = self.count = 0

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
        #print('finding solution at index {} with numVariables {}'.format(index, numVariables))
        if index == numVariables:
            self.sol += 1
            if self.count < 0:
                print('index is numVariables')
                print(map(lambda x: x.printDomain(), self.vars))
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
                if self.count < 0:
                    print('instantiating at index {} with var {}'.format(index, cur_domain[i]))
                    self.count += 1
                self.nodes += 1
                success = self.findOneSolution(index, numVariables)
            for j in range(index, numVariables):
                try:
                    self.vars[j] = saved_vars[j]
                except IndexError:
                    print('Index Error: j is {}, index is {}, self.vars is {}, saved_vars is {}'.format(j, index, self.vars, saved_vars))
            if success:
                if self.count < 0:
                    print('breaking with vars {}'.format(self.vars))
                break

        if success and self.count < 0:
            print('successful, vars {}'.format(self.vars))
            print('got success, index {}'.format(index-1))
        cur_var.setDomain(cur_domain)

        if not success:
            self.bts += 1
            return False
        else:
            return True

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
                print('failing variable at line 272 is {}'.format(self.vars[i]))
                return False
        return True

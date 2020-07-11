class Beta:
    def __init__(self, rules, variables,children, varchecks, leftmemory, rightmemory, leftparent, rightparent):
        self.rules=rules
        self.variables=variables
        self.children=children
        self.varchecks=varchecks
        self.leftmemory=leftmemory
        self.rightmemory=rightmemory
        self.leftparent=leftparent
        self.rightparent=rightparent

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.rules)  + ": " + str(self.variables) + ": " + str(self.children) + ": " + str(self.varchecks) + ": " + str(self.leftmemory)
        + ": " + str(self.rightmemory)

'''
rules : Corresponding rules, for which the beta node corresponds to when firing
variables: List of variables passed down to that beta node from alpha network
children : Reference to other beta nodes to which the current beta node is the parent
varchecks: The list of conditions that need to be checked at this beta node
leftmemory: To accomodate for WME's coming from left parent
rightmemory: To accomodate for WME's coming from right parent
leftparent,rightparent: Reference to left and right parents respectively

'''
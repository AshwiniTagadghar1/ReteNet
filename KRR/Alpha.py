class Alpha:
    def __init__(self,attribute,value,operator,variables,memory,children,rules,isVar):
        self.attribute=attribute
        self.value=value
        self.operator=operator
        self.variables=variables
        self.memory=memory
        self.children=children
        self.rules=rules
        self.isVar=isVar

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.attribute) + ": " + str(self.value)+ ": " + str(self.operator)+ ": " + str(self.variables)+ ": " + str(self.memory) + ": " + str(self.children) + ": " + str(self.rules) + ": " + str(self.isVar)

'''
memory : To accomodate WMEs
children : list of references to the children to the current alpha node
rules : List of rules to which this alpha node corresponds to
isVar:To indicate whether the pattern in alpha node contains a variable or a constant

'''
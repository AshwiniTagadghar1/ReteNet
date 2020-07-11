import xml.etree.ElementTree as ET
from collections import defaultdict
from Alpha import Alpha
from Beta import Beta
from graphviz import Digraph,Source
import warnings
import os

os.environ["PATH"] += os.pathsep + 'C:\Program Files (x86)\Graphviz2.38\bin'

# global variables that help in naming and accessing nodes for graphviz.
count = 0
my_dict = {}


# This function returns the reference to the root tag of the xml ficdle interpreted in a tree structured manner.
def parseXMLFile(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root


treeRoot = parseXMLFile('PSYS-03-out.xml')

#This function finds the correct operator to be used for variable checking at a beta node. It follows the convention 'leftoperand operator rightoperand'
#So if the relevant operator is in the right branch, it is inverted(Eg: > becomes <) and that is returned as the operator
def findOperator(operator1, operator2):
    if (operator1 == '=' and operator2 == '<'):
        return '>'
    elif (operator1 == '<' and operator2 == '='):
        return '<'
    elif (operator1 == '=' and operator2 == '<='):
        return '>='
    elif (operator1 == '<=' and operator2 == '='):
        return '<='
    elif (operator1 == '=' and operator2 == '='):
        return '='
    elif (operator1 == '=' and operator2 == '>'):
        return '<'
    elif (operator1 == '>' and operator2 == '='):
        return '>'
    elif (operator1 == '=' and operator2 == '>='):
        return '<='
    elif (operator1 == '>=' and operator2 == '='):
        return '>='
    elif (operator1 == '!=' or operator2 == '!='):
        return '!='
    elif (operator1 == '<>' or operator2 == '<>'):
        return '<>'
    elif (operator1 == 'or' or operator2 == 'or'):
        return 'or'
    elif (operator1 == '||' or operator2 == '||'):
        return '||'
    elif (operator1 == '|' or operator2 == '|'):
        return '|'
    elif (operator1 == 'and' or operator2 == 'and'):
        return '<>'
    elif (operator1 == '&&' or operator2 == '&&'):
        return '&&'
    elif (operator1 == '&' or operator2 == '&'):
        return '&'


# A function that resolves the condition checking operators from two different branches on the same variable.
def createVarChecks(varlist1, varlist2):
    varchecks = []
    for element1 in varlist1:
        for element2 in varlist2:
            if (element1[0] == element2[0] and element1[1] == element2[1]):
                varchecks.append([element1[0], element1[1], findOperator(element1[2], element2[2])])

    return varchecks


def notPresent(variables, attr, val, op):
    for element in variables:
        if (element[0] == attr and element[1] == val and element[2] == op):
            return 0
    return 1

#This function is used to merge the variables from the parents at a beta node, so that they can be accessed by other beta nodes which are its children.
def mergeVariables(varlist1, varlist2):
    variables = []

    # adding the variables in the left parent branch and also the common variables
    for element1 in varlist1:
        flag = 0
        for element2 in varlist2:
            if (element1[0] == element2[0] and element1[1] == element2[1]):
                if (notPresent(variables, element1[0], element1[1], element1[2])):
                    flag = 1
                    variables.append([element1[0], element1[1], findOperator(element1[2], element2[2])])
                    break
        if (flag == 0):
            if (notPresent(variables, element1[0], element1[1], element1[2])):
                variables.append([element1[0], element1[1], element1[2]])

    # adding the variales which are exclusive to the right parent branch
    for element2 in varlist2:
        flag = 0
        for element1 in varlist1:
            if (element1[0] == element2[0] and element1[1] == element2[1]):
                flag = 1
                break
        if (flag == 0):
            if (notPresent(variables, element2[0], element2[1], element2[2])):
                variables.append([element2[0], element2[1], element2[2]])

    return variables


# A function that constructs the beta network, where a beta node joins two alpha nodes utmost.
def createBetaNetwork(ruleBranches):
    for key, value in ruleBranches.items():
        beta = Beta(set(), [], [], [], [], [], [], [])
        beta.rules.add(key)

        # create beta nodes if the number of leaf alpha nodes for a rule is >1.
        if (len(value) > 1):
            alphanode1 = value[0]
            alphanode2 = value[1]
            alphanode1.children.append(beta)
            alphanode2.children.append(beta)
            beta.leftparent = alphanode1
            beta.rightparent = alphanode2
            beta.varchecks.extend(createVarChecks(alphanode1.variables, alphanode2.variables))
            beta.variables = mergeVariables(alphanode1.variables, alphanode2.variables)
            previousBeta = beta
            for alphanode in value[2:]:
                beta = Beta(set(), [], [], [], [], [], [], [])
                beta.rules.add(key)
                previousBeta.children.append(beta)
                alphanode.children.append(beta)
                beta.leftparent = previousBeta
                beta.rightparent = alphanode
                beta.varchecks = createVarChecks(previousBeta.variables, alphanode.variables)
                beta.variables = mergeVariables(previousBeta.variables, alphanode.variables)
                previousBeta = beta
        #creating beta nodes in the case where there is only one parent alpha node i.e. the rule has only one WME condition
        else:
            alphanode1 = value[0]
            alphanode1.children.append(beta)
            beta.leftparent = alphanode1


# The function that constructs the Rete Network and ouputs a png file containing the network graph.
def ReteNet_Visualize(root):
    global count, my_dict
    dot = Digraph(comment='ReteNet Visulization')
    visited = {}
    queue = []
    queue.append(root)
    visited[root] = True

    while queue:
        s = queue.pop(0)
        root = s
        if (isinstance(root, Alpha)):
            parent = "α:<" + str(root.attribute) + "," + str(root.value) + "," + str(root.operator) + "> "
        else:
            parent = "β:<" + "," + str(root.varchecks) + str(root.rules) + "> "
        if (root not in list(my_dict.values())):
            my_dict[count] = root
            P = str(count)
            dot.node(P, parent)
            count = count + 1
        else:
            P = str(list(my_dict.keys())[list(my_dict.values()).index(root)])

        for child in root.children:
            if (isinstance(child, Alpha)):
                son = "α:<" + str(child.attribute) + "," + str(child.value) + "," + str(child.operator) + "> "
            else:
                son = "β:<" + "," + str(child.varchecks) + str(child.rules) + "> "
            if (child not in list(my_dict.values())):
                my_dict[count] = child
                C = str(count)
                dot.node(C, son)
                count = count + 1
                dot.edge(P, C)
            else:
                C = str(list(my_dict.keys())[list(my_dict.values()).index(child)])
                dot.edge(P, C)

            if child not in visited:
                queue.append(child)
                visited[child] = True

    src = Source(dot.source)
    src.render('test-output/rete', format='png', view=True)

#Creates the alpha network of the Rete net.
def createAlphaNetwork(root, attrlist, ruleCount):
    for i in range(len(attrlist)):
        attribute = attrlist[i][0]
        value = attrlist[i][1]
        operator = attrlist[i][2]
        isVar = attrlist[i][3]
        flag = 0
        for child in root.children:
            if (child.attribute == attribute and child.value == value and child.operator == operator):
                flag = 1
                root = child
                child.rules.add(ruleCount)
                break
        if (flag == 0):
            if (isVar):
                child = Alpha(attribute, value, operator, [], 0, [], set(), 1)
                if (root.variables):
                    child.variables.extend(root.variables)
                child.variables.append([attribute, value, operator])
            else:
                child = Alpha(attribute, value, operator, [], 0, [], set(), 0)
                if (root.variables):
                    child.variables.extend(root.variables)
            child.rules.add(ruleCount)
            root.children.append(child)
            root = child
    ruleBranches[ruleCount].append(child)


#main part of the progrqam,includes code to parse XML and create appropriate representations.
warnings.filterwarnings("ignore")
root = Alpha("root", 0, '=', [], 0, [], set(), 0)
varString = "VARIABLE"
ruleCount = 0
ruleBranches = defaultdict(list)
for rules in treeRoot.findall("IF"):
    ruleCount += 1
    for wme in rules.find("CONDITIONS").findall("WME"):
        attrlist = []
        className = wme.find("TYPE").attrib["text"]
        attrlist.append(["class", className, '=', 0])
        attributes = wme.findall("ATTRIBUTE")
        for element in attributes:
            subattributes = element.findall("*/ATTRIBUTE")
            if (len(subattributes) == 0):
                attribute = element.attrib["text"]
                value = element.getchildren()[0].attrib["text"]
                text = element.getchildren()[0].tag
                operator = '='
            else:
                subattribute = subattributes[0]
                opNode = element.getchildren()[0]
                operator = element.getchildren()[0].attrib["text"]
                attribute = opNode.getchildren()[0].attrib["text"]
                value = opNode.getchildren()[1].attrib["text"]
                text = opNode.getchildren()[1].tag
            isVar = 0
            if (text == varString):
                isVar = 1
            attrlist.append([attribute, value, operator, isVar])
        createAlphaNetwork(root, attrlist, ruleCount)

# defining beta network
createBetaNetwork(ruleBranches)

# Visulizing the ReteNet
ReteNet_Visualize(root)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:46:23 2019

@author: ajshah
"""

import puns.Constants
import numpy.random as random


def SampleFormula(depth, vocabulary):


    if depth ==1:
        return [random.choice(vocabulary)]
    else:
        #Sample a production rule
        Op = random.choice(list(Constants.Operators | set(['true','false']) | set(['atom'])))

        if Op == 'atom':
            return [random.choice(vocabulary)]

        if Op in set(['true','false']):
            return [Op]

        if Op in Constants.BinaryOperators:
            return [Op,SampleFormula(depth-1, vocabulary), SampleFormula(depth-1,vocabulary)]
        else:
            return [Op, SampleFormula(depth-1,vocabulary)]


def GetTraceSlice(Signal,t):
    if t >= Signal['length']:
        raise Exception('Requested time stamp exceeds trace length')
    else:
        SignalSlice = {}
        for key in (set(Signal.keys()) - set(['length'])):
            SignalSlice[key] = Signal[key][t]
        return SignalSlice




def GetVocabulary(formula, vocab = set()): #Get all the proposition leaf nodes in a formula

    if IsAtom(formula[0]):
        return vocab|set([formula[0]])
    elif formula[0] in Constants.Literals:
        return vocab
    else:
        for subformula in formula[1::]:
            vocab = GetVocabulary(subformula, vocab)
        return vocab


def IsAtom(s):
    if s not in (Constants.Operators | Constants.Literals):
        return True
    else:
        return False

def IsAtom2(s):
    return(IsAtom(s[0]), s)

def VerifyFormulaSyntax(formula):
    ''' This function verifies that the formula adheres to the defined syntax'''

    if not isinstance(formula, list):
        return (False, formula) #The formula must always be a list


    if IsAtom(formula[0]) or formula[0] in Constants.Literals:
        if len(formula)==1:
            return (True,'Atom')
        else:
            return (False, formula)

    #Check the unary operators have only a single argument
    if formula[0] in Constants.UnaryOperators:
        #Check that the unary operator actually has only a single operator
        if len(formula) != 2:
            return (False, formula) # Too many or too few arguments
        else:
            (flag, subformula) = VerifyFormulaSyntax(formula[1])
            if flag:
                return (True,'Unary')
            else:
                return (False, subformula)

    if formula[0] in set(['and','or']):
        if len(formula) < 3:  #too few arguments
            return (False, formula)
        else: #Correct number of arguments, check if the subformulas are valid

            for sub in formula[1::]:

                (flag, subformula) = VerifyFormulaSyntax(sub)
                if not flag:
                    return (False, subformula)

            return (True,'AndOr')

    if formula[0] in set(['U','wU','R','imp']): #binary operators
        if len(formula) != 3:
            return (False, formula)
        else:
            for sub in formula[1::]:
                (flag, subformula) = VerifyFormulaSyntax(sub)
                if not flag:
                    return (False, subformula)
            return (True, 'Binary')

def CheckSpecialSyntax(formula, special_syntax):
    flag,sub  = VerifyFormulaSyntax(formula)
    if not flag:
        print('Formula not a valid LTL formula')
        return (False,formula)

    #Create default syntax
    syntax = {}
    syntax['operators'] = special_syntax['operators']
    syntax['production' ] = {}
    for key in syntax['operators']:
        syntax['production'][key] = lambda x: CheckSpecialSyntax(x,special_syntax)
    for key in special_syntax['production']:
        syntax['production'][key] = special_syntax['production'][key]

    for key in syntax['operators']:
        if type(syntax['production'][key])==list:
            for i in range(len(syntax['production'][key])):
                if syntax['production'][key][i] == None:
                    syntax['production'][key][i] = lambda x: CheckSpecialSyntax(x,special_syntax)

    #return syntax

    # If the operator is an atomic proposition return true
    # If it is a connective, check if the connective is within the special syntax
    # If the connective is within special syntax, check whether the arguments satisfy the special production rules

    if IsAtom(formula[0]):
        return (True, 'atom')
    else:

        if formula[0] not in syntax['operators']:
            return (False, formula) #operator out of syntax
        else:
            # operator in syntax, now check if the subformulas are in syntax as well
            if type(syntax['production'][formula[0]]) == list:
                CheckFunctions = syntax['production'][formula[0]]
            else:
                CheckFunctions = [syntax['production'][formula[0]]]*len(formula[1::]) #apply the same check function to all arguments

            for i in range(len(CheckFunctions)):
                (flag, sub) = CheckFunctions[i](formula[i+1])
                if flag == False:
                    return (False, sub)

            # All the subformula conform to the grammar return true
            return (True,'Checked')




def IsCoSafe(formula):
    return CheckSpecialSyntax(formula, CoSafeSyntax)


def IsSafe(formula):
    return CheckSpecialSyntax(formula, SafeSyntax)


'''Note that both safe and co-safe formulas must satisfy the LTL syntax. So verify the syntax first, and then just c
heck for operators
'''

CoSafeSyntax = {}
CoSafeSyntax['operators'] = set(['true', 'not','and','or','imp','X','F','U'])
CoSafeSyntax['production'] = {}
CoSafeSyntax['production']['not'] = [IsAtom2]
CoSafeSyntax['production']['imp'] = [IsAtom2, None]

SafeSyntax = {}
SafeSyntax['operators'] = ['false','not','and','or','imp','X','G','R']
SafeSyntax['production'] = {}
SafeSyntax['production']['not'] = [IsAtom2]
SafeSyntax['production']['imp'] = [IsAtom2, None]


if __name__ == '__main__':
    formula = ['wU', ['not', ['R', ['and', ['P2'], ['P2']], ['U', ['sand'], ['P2']]]], ['R', ['or', ['true'], ['false']], ['sea']]]

    VerifyFormulaSyntax(formula)
    syntax = CheckSpecialSyntax(formula, CoSafeSyntax)
    formula = ['not',['F',['a']]]
    IsCoSafe(formula)

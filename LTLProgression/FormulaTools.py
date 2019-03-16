#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:46:23 2019

@author: ajshah
"""

import Constants
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


    

def GetVocabulary(formula, vocab): #Get all the proposition leaf nodes in a formula
    
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

    
def IsCoSafe(formula):
    a=1
    
    
def IsSafe(formula):
    a=1

if __name__ == '__main__':
    formula = ['wU', ['not', ['R', ['and', ['P2'], ['P2']], ['U', ['sand'], ['P2']]]], ['R', ['or', ['true'], ['false']], ['sea']]]

    VerifyFormulaSyntax(formula)
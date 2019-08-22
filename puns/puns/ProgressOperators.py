#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:48:37 2019

@author: ajshah
"""

import puns.Constants as Constants
from puns.FormulaTools import *


def ProgressU(formula, SignalSlice, final):
    Subformula2 = ReduceFormula(['and', ProgressSingleTimeStep(formula[1], SignalSlice, final), formula])
    NewFormula = ReduceFormula(['or', ProgressSingleTimeStep(formula[2],SignalSlice, final), Subformula2])
    return NewFormula


def ProgressF(formula, SignalSlice, final):
    return ReduceFormula(['or', ProgressSingleTimeStep(formula[1], SignalSlice, final), formula])


def ProgressG(formula, SignalSlice, final):
    return ReduceFormula(['and',ProgressSingleTimeStep(formula[1], SignalSlice, final), formula])


def ProgressAnd(formula, SignalSlice, final):
    subformulas = []

    for val in formula[1::]:

        prog_subformula = ProgressSingleTimeStep(val, SignalSlice, final)
        if prog_subformula[0] == False: #If any subformula is false progress entire thing to false
            return [False]
        elif prog_subformula[0] == True:
            continue
        else:
            subformulas.append(prog_subformula)

    if len(subformulas)==0: #Everything is false
        prog_formula = [True]
    elif len(subformulas)==1:
        prog_formula = subformulas[0]
    else:
        prog_formula = ['and'] + (subformulas)

    return prog_formula


def ProgressOr(formula, SignalSlice, final):

    subformulas = []

    for val in formula[1::]:

        prog_subformula = ProgressSingleTimeStep(val, SignalSlice, final)
        if prog_subformula[0] == True:
            return [True]
        elif prog_subformula[0] == False:
            continue
        else:
            subformulas.append(prog_subformula)

    if len(subformulas) == 0:
        prog_formula = [False]
    elif len(subformulas) == 1:
        prog_formula = subformulas[0]
    else:
        prog_formula = ['or'] + (subformulas)

    return prog_formula


def ProgressNot(formula, SignalSlice, final):
    return [not ProgressSingleTimeStep(formula[1], SignalSlice, final)[0]]


def ProgressImp(formula, SignalSlice, final):
    NewFormula = ['or',['not',formula[1]], formula[2]]
    return ProgressSingleTimeStep(NewFormula, SignalSlice, final)

def ProgressFinal(formula, SignalSlice):

    if IsAtom(formula[0]):
        return [SignalSlice[formula[0]]]
    if formula[0]=='true' or formula[0] == True: return [True]
    if formula[0]=='false' or formula[0] == False: return [False]

    #Deal with logical operators
    if formula[0] == 'not': return ProgressNot(formula, SignalSlice)
    if formula[0] == 'and': return ProgressAnd(formula, SignalSlice)
    if formula[0] == 'or': return ProgressOr(formula, SignalSlice)
    if formula[0] == 'imp': return ProgressImp(formula, SignalSlice)

    #deal with the temporal operators for the final time step
    if formula[0] == 'X' or formula[0] == 'G' or formula[0] == 'F':
        return ProgressSingleTimeStep(formula[1], SignalSlice)
    if formula[0] == 'U':
        return ProgressSingleTimeStep(formula[2], SignalSlice)



def ProgressSingleTimeStep(formula, SignalSlice, final=False):
        #Deal with literals and atoms
    if IsAtom(formula[0]):
        return [SignalSlice[formula[0]]]
    if formula[0]=='true' or formula[0] == True: return [True]
    if formula[0]=='false' or formula[0] == False: return [False]

    #Deal with logical operators
    if formula[0] == 'not': return ProgressNot(formula, SignalSlice, final)
    if formula[0] == 'and': return ProgressAnd(formula, SignalSlice, final)
    if formula[0] == 'or': return ProgressOr(formula, SignalSlice, final)
    if formula[0] == 'imp': return ProgressImp(formula, SignalSlice, final)

    if final==False:
    #Deal with the temporal operators
        if formula[0] == 'X': return formula[1]
        if formula[0] == 'F': return ProgressF(formula, SignalSlice, final)
        if formula[0] == 'G': return ProgressG(formula, SignalSlice, final)
        if formula[0] == 'U': return ProgressU(formula, SignalSlice, final)
    else:
       if formula[0] == 'X' or formula[0] == 'G' or formula[0] == 'F':
           return ProgressSingleTimeStep(formula[1], SignalSlice, final)
       if formula[0] == 'U':
           return ProgressSingleTimeStep(formula[2], SignalSlice, final)


def ReduceFormula(formula):

    if formula[0] == 'true': formula[0] = True
    if formula[0] == 'false': formula[0] = False

    if formula[0] == 'or': #Remove all the false statement and replace with true if any is true
         if [True] in formula[1::]: return [True]
         subformula = [val for val in formula[1::] if val != [False]]
         if len(subformula) == 0:
             NewFormula = [False]
         elif len(subformula) == 1:
             NewFormula = subformula[0]
         else:
             NewFormula = ['or'] + subformula
         return NewFormula

    if formula[0] == 'and':
        if [False] in formula[1::]: return [False]
        subformula = [val for val in formula[1::] if val !=[True]]
        if len(subformula) == 0:
            NewFormula = [True]
        elif len(subformula) == 1:
            NewFormula = subformula[0]
        else:
            NewFormula = ['and'] + subformula
        return NewFormula
    return formula

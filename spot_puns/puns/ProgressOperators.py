#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:48:37 2019

@author: ajshah
"""

import puns.Constants as Constants
from puns.FormulaTools import *
from spot_wrapper import *


def ProgressU(formula, SignalSlice, final):
    prog_phi1 = ProgressSingleTimeStep(formula[1], SignalSlice, final)
    prog_phi2 = ProgressSingleTimeStep(formula[2], SignalSlice, final)
    return simplify_puns(['or',prog_phi2,['and', prog_phi1, formula]])


def ProgressF(formula, SignalSlice, final):
    return simplify_puns(['or', ProgressSingleTimeStep(formula[1], SignalSlice, final), formula])


def ProgressG(formula, SignalSlice, final):
    return simplify_puns(['and', ProgressSingleTimeStep(formula[1], SignalSlice, final), formula])


def ProgressAnd(formula, SignalSlice, final):
    return simplify_puns(['and'].extend([ProgressSingleTimeStep(f, SignalSlice, final) for f in formula[1:]]))


def ProgressOr(formula, SignalSlice, final):
    return simplify_puns(['or'].extend([ProgressSingleTimeStep(f, SignalSlice, final) for f in formula[1:]]))


def ProgressNot(formula, SignalSlice, final):
    return simplify_puns(['not', ProgressSingleTimeStep(formula[1], SignalSlice, final)])


def ProgressImp(formula, SignalSlice, final):
    prog_phi1 = ProgressSingleTimeStep(formula[1], SignalSlice, final)
    prog_phi2 = ProgressSingleTimeStep(formula[2], SignalSlice, final)
    return simplify_puns(['imp', prog_phi1, prog_phi2])

def ProgressSingleTimeStep(formula, SignalSlice, final=False):
        #Deal with literals and atoms
    if IsAtom(formula[0]):
        return ['true'] if SignalSlice[formula[0]] else ['false']
    if formula[0]=='true' or formula[0] == True: return ['true']
    if formula[0]=='false' or formula[0] == False: return ['false']

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
       

if __name__ == '__main__':
    formula = ['F',['p']]
    TraceSlice = {}
    TraceSlice['p'] = True
    formula = ProgressSingleTimeStep(formula, TraceSlice)


# def ProgressFinal(formula, SignalSlice):

#     if IsAtom(formula[0]): return [SignalSlice[formula[0]]]
#     if formula[0]=='true' or formula[0] == True: return [True]
#     if formula[0]=='false' or formula[0] == False: return [False]

#     #Deal with logical operators
#     if formula[0] == 'not': return ProgressNot(formula, SignalSlice)
#     if formula[0] == 'and': return ProgressAnd(formula, SignalSlice)
#     if formula[0] == 'or': return ProgressOr(formula, SignalSlice)
#     if formula[0] == 'imp': return ProgressImp(formula, SignalSlice)

#     #deal with the temporal operators for the final time step
#     if formula[0] == 'X' or formula[0] == 'G' or formula[0] == 'F':
#         return ProgressSingleTimeStep(formula[1], SignalSlice)
#     if formula[0] == 'U':
#         return ProgressSingleTimeStep(formula[2], SignalSlice)
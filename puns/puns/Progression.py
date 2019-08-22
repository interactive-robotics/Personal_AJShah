#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:53:40 2019

@author: ajshah
"""


import puns.Constants as Constants
from collections import deque
from puns.FormulaTools import *
from puns.ProgressOperators import *
import numpy.random as random
import numpy as np
from itertools import product
from functools import reduce
import networkx as nx
import pygraphviz as pgv
import json
from matplotlib.colors import Colormap


def CreateSpecificationMDP(Formulas, Probs, risk_level=0.95):

    a=1

def Progress(formula, Signal, t=None):

    if t==None:
        t = Signal['length'] #By Default progress the sequence through the entire trace
    #First verify that the signal and formula vocabulary match
    if GetVocabulary(formula, set()).issubset(set(Signal.keys())|set([True, False])-set(['length'])): #Vocab check

        for i in range(t-1): #Progress till the penultimate time step
            SignalSlice = GetTraceSlice(Signal, i)
            formula = ProgressSingleTimeStep(formula,SignalSlice)

        if t<Signal['length']:
            SignalSlice = GetTraceSlice(Signal,t-1)
            formula = ProgressSingleTimeStep(formula, SignalSlice)
        else:
            SignalSlice = GetTraceSlice(Signal,t-1)
            formula = ProgressSingleTimeStep(formula, SignalSlice, final=True)
        return formula

    else:
        raise Exception('Formula and signal vocabulary mismatch')



def VerifyVocabulary(formula, signal):
    formula_vocabulary = GetVocabulary(formula, set())

    return formula_vocabulary.issubset(set(signal.keys())|set([True, False]))




def get_all_truth_assignments(vocabulary):
    n_propositions = len(vocabulary)
    propositions = sorted(list(vocabulary))
    All_assignments = []

    possible_truth_assignments = list(product(*([True, False],)*n_propositions))
    for val in possible_truth_assignments:
        temp_assignment = {}
        for (key,value) in zip(propositions, val):
            temp_assignment[key] = value
        All_assignments.append(temp_assignment)

    return All_assignments

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:53:40 2019

@author: ajshah
"""


import Constants
from collections import deque
from FormulaTools import *
from ProgressOperators import *
import numpy.random as random
import numpy as np
from itertools import product
import json


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



def FindAllProgressions(formula):
    
    queue = deque([formula])
    visited = [formula]
    edges = {}
    progression_states = {}
    progression_states[json.dumps(formula)] = 0
    
    while queue:
        
        new_formula = queue.pop()
        vocabulary = GetVocabulary(new_formula)
        truth_assignments = get_all_truth_assignments(vocabulary)
        
        for truth_assignment in truth_assignments:
            progressed_formula = ProgressSingleTimeStep(new_formula, truth_assignment)
            edge = (json.dumps(new_formula), json.dumps(progressed_formula))
            if edge not in edges:
                edges[edge] = []
            edges[edge].append(truth_assignment)
            
            if progressed_formula not in visited:
                visited.append(progressed_formula)
                progression_states[json.dumps(progressed_formula)]=len(progression_states)
                queue.appendleft(progressed_formula)
        
    edge_tuples = []
    for edge in edges:
        edge_tuples.append((json.loads(edge[0]), json.loads(edge[1]), edges[edge]))
    return progression_states, edge_tuples

def IdentifyTerminalStates(progression_states):
    formulas = list(map(json.loads, progression_states.keys()))
    terminal_states = [json.dumps([True]), json.dumps([False])]
    for formula in formulas:
        if IsSafe(formula)[0]:
            terminal_states.append(json.dumps(formula))
    
    return terminal_states
    
    
    
    
    

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

if __name__ == '__main__':
    
    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas = np.array(Formulas)
    Prob = np.array(Prob)
    Formulas = Formulas[idx]
    Prob = Prob[idx]
    formula = Formulas[0]
    #print(formula)
    
    SignalSlice = GetTraceSlice(SampleSignal,0)
    progressed_formula = ProgressSingleTimeStep(formula, SignalSlice)
    AllProgressions, AllEdges = FindAllProgressions(progressed_formula)
    TerminalStates = IdentifyTerminalStates(AllProgressions)
    
    
    

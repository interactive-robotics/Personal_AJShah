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




def CreateReward_min_regret(probs):
    #note that the probs must be marginal probabilities of all formulas. The state description might include fewer states
    #Thus np.sum(probs) = 1
    #and len(probs) == len(state)
    
    #This should return a function of the state that will generate the reward for entering that state. The max reward is 1
    #The minimum possible reward is -1
    
    def Reward(state):
        
        if len(probs) >= len(state):
            #Select the probabilisties of the states being considered
            sel_probs = np.array(probs[0:len(state)])
            sel_probs = sel_probs/np.sum(sel_probs)
            #Check if the state is a reward giving state
            if IsTerminalState(state):
                #select the non-falsified formula
                verified_states = np.array([1 if formula != '[false]' else -1 for formula in state])
                return np.sum((np.multiply(verified_states, sel_probs)))
            else:
                return 0
        else:
            raise Exception('Dimension mismatch between probabilities and state length')
    return Reward
            
    

def FindAllProgressions(formulas):
    
    initial_state = tuple(json.dumps(formula) for formula in formulas)
    progression_states = {}
    progression_states[initial_state] = 0
    visited = [initial_state]
    queue = deque([initial_state])
    edges = {}
    
    while queue:
        
        state = queue.pop()
        Formulas = [json.loads(formula) for formula in state]
        #Determine the overall vocabulary
        vocabulary = reduce(
                            lambda vocab, form: GetVocabulary(form, vocab),
                            Formulas,
                            set())
        truth_assignments = get_all_truth_assignments(vocabulary)
        
        for truth_assignment in truth_assignments:
            
            progressed_formulas = [ProgressSingleTimeStep(formula, truth_assignment) for formula in Formulas]
            progressed_state = tuple(json.dumps(progressed_formula) for progressed_formula in progressed_formulas)
            edge = (state, progressed_state)
            
            if edge not in edges:
                edges[edge] = []
                
            edges[edge].append(truth_assignment)
            
            if progressed_state not in visited:
                visited.append(progressed_state)
                progression_states[progressed_state] = len(progression_states)
                queue.appendleft(progressed_state)
        
    edge_tuples = []
    for edge in edges:
        edge_tuples.append((edge[0], edge[1], edges[edge]))
    
    return progression_states, edge_tuples
    


def FindAllProgressions_single_formula(formula):
    
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

def VerifyVocabulary(formula, signal):
    formula_vocabulary = GetVocabulary(formula, set())
    
    return formula_vocabulary.issubset(set(signal.keys())|set([True, False]))

def IsTerminalState(state):
    return reduce(lambda memo, formula: memo and IsTerminal(json.loads(formula)), state, True)

def IsTerminal(formula):
    return json.dumps(formula) in set([json.dumps([True]),json.dumps([False])]) or IsSafe(formula)[0]


def FindTerminalStates_single_formula(progression_states):
    terminal_states = [state for state in progression_states if IsTerminal(json.loads(state))]
    return terminal_states

def FindTerminalStates(progression_states):
    terminal_states = []
    for state in progression_states:
        if reduce(lambda memo, formula: memo and IsTerminal(json.loads(formula)), state, True):
            terminal_states.append(state)
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

def VisualizeProgressionStates(progression_states, edge_tuples, RewardFun, single_formula = False, terminal_states = [], 
                               colormap='reward'):
    
    G = nx.DiGraph()
    colors = {}
    for node in progression_states:
        G.add_node(progression_states[node])
        if colormap == 'terminal':
            colors[progression_states[node]] = 1 if node in terminal_states else 0
        elif colormap == 'reward':
            colors[progression_states[node]] = RewardFun(node)
        else:
            colors[progression_states[node]] = 0 #All nodes have the same color
    for edge in edge_tuples:
        e = (json.dumps(edge[0]), json.dumps(edge[1])) if single_formula else edge
        G.add_edge(progression_states[e[0]], progression_states[e[1]])
        
    colors = [colors[node] for node in G.nodes()]
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw_networkx(G, pos, with_label=True, node_color = colors, cmap = 'coolwarm_r', vmin=-1.2, vmax=1.2)
    return G, colors

if __name__ == '__main__':
    
    '''Import Synthetic Domain data'''
    
    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    TraceSlice = GetTraceSlice(SampleSignal,0)
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas_synth = np.array(Formulas)[idx]
    Probs_synth = np.array(Prob)[idx]
    ProgressedFormulas_synth = np.array([ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas_synth])
    
    
    '''Finding progression states'''
    ProgressedFormulas = {'synth': ProgressedFormulas_synth,}
    Probs = {'synth': Probs_synth,}
    Formulas = {'synth': Formulas_synth,}
    
    progression_states = {}
    edges = {}
    terminal_states = {}
    Domain = {'synth': 'Synthetic Domain', 'dinner': 'Dinner Table Domain'}

    keys = ['synth',]
    for key in keys:
        domain = Domain[key]
        print(f'Finding progression states for {domain}')
        progression_states[key], edges[key] = FindAllProgressions(ProgressedFormulas[key][0:100])
        terminal_states[key] = FindTerminalStates(progression_states[key])
        print(f'Number of unique progressions in {domain}: ', len(progression_states[key]))
        print(f'Number of edges in {domain}: ', len(edges[key]))
        print(f'Number of terminal states in {domain}: ', len(terminal_states[key]),'\n')
    
    '''Testing progression graph visualization'''
    RewardFun = CreateReward_min_regret(Probs['synth'])
    G,colors = VisualizeProgressionStates(progression_states['synth'], edges['synth'], RewardFun, 
                                          terminal_states = terminal_states['synth'])

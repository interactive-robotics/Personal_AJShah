#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 18:48:37 2019

@author: ajshah
"""

import Constants
from SpecificationMDP import *

def CreateSampleMDP():
    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    TraceSlice = GetTraceSlice(SampleSignal,0)
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas_synth = np.array(Formulas)[idx]
    Probs = np.array(Prob)[idx]
    ProgressedFormulas = np.array([ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas_synth])
    
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type='min_regret', risk_level=0.3)
    control_mdp = SyntheticMDP(5,4)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP

def CreateSpecMDP(PathToSpec, n_threats, n_waypoints, accessibility=None):
    
    if accessibility == None: accessibility = [True]*n_waypoints
    
    control_mdp = SyntheticMDP(n_threats, n_waypoints, accessibility)
    
    Data = json.load(open(PathToSpec,'r'))
    Formulas = Data['support']
    Probs = Data['probs']
    
    TraceSlice = {}
    for i in range(n_threats):
        TraceSlice[f'T{i}'] = False
    for i in range(n_waypoints):
        TraceSlice[f'W{i}'] = False
        TraceSlice[f'P{i}'] = accessibility[i]
    
    ProgressedFormulas = [ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas]
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type='min_regret')
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP
    

if __name__ == '__main__':
    MDP= CreateSpecMDP('ExampleSpecs2.json',5,5)
    MDP.specification_fsm.visualize(prog = 'twopi')
    

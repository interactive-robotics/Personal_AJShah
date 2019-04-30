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

if __name__ == '__main__':
    MDP = CreateSampleMDP()
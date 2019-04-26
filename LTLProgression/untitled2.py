#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 11:34:22 2019

@author: ajshah
"""

from SpecificationFSMTools import *
from copy import deepcopy
import matplotlib
#%matplotlib inline
matplotlib.rcParams['figure.figsize'] = [16,9]

if __name__ == '__main__':
    Formulas = {}
    Probs = {}
    
    #Case 1 most likely is also the most restrictive
    
    Formulas[1] = []
    Formulas[1].append(['and',['F',['A']],['F',['B']],['F',['C']]])
    Formulas[1].append(['and',['F',['A']],['F',['B']]])
    Formulas[1].append(['F',['A']])
    
    #check whether each is a valid formula
    validity = reduce(lambda memo, formula: memo and VerifyFormulaSyntax(formula)[0], Formulas[1], True)
    print('Formula[1] specification set is:', validity)
    Probs[1] = [0.7, 0.2, 0.1]
    
    Formulas[2] = []
    Formulas[2] = deepcopy(Formulas[1])
    Probs[2] = [0.1, 0.2, 0.7] # Lease restrictive is most likely
    
    Formulas[3] = []
    Formulas[3].append(['F',['A']])
    Formulas[3].append(['F',['B']])
    Formulas[3].append(['F',['C']])
    validity = reduce(lambda memo, formula: memo and VerifyFormulaSyntax(formula)[0], Formulas[3], True)
    print('Formula[3] specification set is:', validity)
    Probs[3] = [0.3,0.4,0.3]
    
    Formulas[4] = []
    Formulas[4].append(['and',['F',['A']],['G',['not',['C']]]])
    Formulas[4].append(['and',['F',['B']],['G',['not',['C']]]])
    Formulas[4].append(['F',['C']])
    validity = reduce(lambda memo, formula: memo and VerifyFormulaSyntax(formula)[0], Formulas[4], True)
    print('Formula[4] specification set is:', validity)
    Probs[4] = [0.2,0.2,0.6]
    
    spec_fsm_map = {}
    spec_fsm_max_cover = {}
    spec_fsm_min_regret = {}
    spec_fsm_cc = {}
    
    for i in [1,2,3,4]:
        print(i)
        if i==3:
            a=1
        spec_fsm_map[i] = SpecificationFSM(Formulas[i], Probs[i], reward_type='map')
        spec_fsm_max_cover[i] = SpecificationFSM(Formulas[i], Probs[i], reward_type='max_cover')
        spec_fsm_min_regret[i] = SpecificationFSM(Formulas[i], Probs[i], reward_type='min_regret')
        for failure_prob in [0.25, 0.5, 0.75]:
            spec_fsm_cc[(i,failure_prob)] = SpecificationFSM(Formulas[i], Probs[i], reward_type='chance_constrained', risk_level=failure_prob)
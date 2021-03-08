# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 15:47:37 2021

@author: AJShah
"""

from pedagogical_demo import *
from query_selection import *
from Auto_Eval_Active import *
from tqdm import tqdm
import os
import dill

directory =  'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'

def find_query_mismatches(d, strat1, strat2):
    
    diverging_dists = []
    
    for i in tqdm(d['results'].keys()):
        for c in set(d['results'][i].keys()) - set(['ground_truth']):
            for q in range(len(d['results'][i][c])):
                
                dist = d['results'][i][c][q]
                spec_fsm = SpecificationFSM(dist['formulas'], dist['probs'])
                
                s1 = identify_desired_state(spec_fsm, query_type = strat1)
                s2 = identify_desired_state(spec_fsm, query_type = strat2)
                
                if s1 != s2:
                    diverging_dists.append({'dist': dist})
                    if s1 != spec_fsm.id2states[0] and s2 != spec_fsm.id2states[0]:
                        diverging_dists[-1]['trivial'] = False
                    
    return diverging_dists
                

if __name__ == '__main__':
    
    print('Reading Results file \n')
    with open(os.path.join(directory, 'active_paired_summary.pkl'),'rb') as file:
        d = dill.load(file)
        
    
    print('Detecting Diverging queries')
    dists = find_query_mismatches(d, 'uncertainty_sampling', 'info_gain')
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 15:47:37 2021

@author: AJShah
"""

from pedagogical_demo import *
from query_selection import *
from Auto_Eval_Active import *
import os
import dill

directory =  'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'

def import_data ():
    
    with open(os.path.join(directory, 'example.pkl'), 'rb') as file:
        data = dill.load(file)
    return data

if __name__ == '__main__':
    
    data = import_data()
    dist = data['Distributions'][0]
    
    spec_fsm = SpecificationFSM(dist['formulas'], dist['probs'])
    ground_truth = data['ground_truth_formula']
    
    d = compute_expected_entropy_gain_noisy_pedagogical(spec_fsm, debug = True)
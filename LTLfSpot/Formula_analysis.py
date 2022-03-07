# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:44:10 2022

@author: AJShah
"""

from formula_sampler import *

def sample_formula_path_length(n_form= 25, path_length = 2):
    
    formulas = []
    
    while len(formulas) < n_form:
        formula = sample_formula()
        if preferred_path_length(formula) == path_length:
            formulas.append(formula)
    
    return formulas

if __name__ == '__main__':
    
    #Sample 100 formulas for given path length
    path_length = 2
    n_form = 25
    
    formulas = sample_formula_path_length(n_form, path_length)
    preferred_path_lengths = [2]*len(formulas)
    fail_paths = [failure_paths(f) for f in formulas]
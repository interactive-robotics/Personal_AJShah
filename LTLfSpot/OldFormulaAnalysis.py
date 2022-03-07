# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:25:39 2022

@author: AJShah
"""

from formula_sampler import *

def read_formulas():
    with open('OldFormulas.txt','r') as file:
        formulas = file.readlines()
    
    formulas = [f.rstrip('\n') for f in formulas]
    return formulas

if __name__ == '__main__':
    
    formulas = read_formulas()
    data = []
    
    for f in formulas:
        record = {}
        record['formula'] = f
        record['path_length'] = preferred_path_length(f)
        record['fail_paths'] = failure_paths(f)
        data.append(record)
    
    for r in data:
        print(record['formula'],record['path_length'], record['fail_paths'])
        
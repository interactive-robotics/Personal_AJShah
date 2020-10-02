#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 16:06:51 2020

@author: ajshah
"""

import pandas as pd

def read_experiment_dataset(Path, exclude_batch = False):
    task1, task2 = get_task_assignments()
    subject_files = os.listdir(Path)
    
    data = {}
    i=0
    for subj_dir in subject_files:
        
        if subj_dir.split('_')[0] == 'subject':
            
            subjID = int(subj_dir.split('_')[1])
            
            if subjID in discard:
                continue
            else:
                data[subjID] = {}
                Protocol = subj_dir.split('_')[-1]
                if exclude_batch and Protocol == 'Random':
                    continue
                else:
                    data[subjID]['subjID'] = subjID
                    data[subjID]['Protocol'] = Protocol
                    dist = read_distribution(subjID, Protocol)
                    #data[subjID]['Similarity'] = compare_distribution(, distribution)
                    #data[subjID]['dist'] = read_distribution(subjID, Protocol)
                    data[subjID]['Task'] = 'Task 1' if subjID in task1 else 'Task 2'
                    true_formula = task1_formula if subjID in task1 else task2_formula
                    data[subjID]['Similarity'] = compare_distribution(true_formula, dist)
                    data[subjID]['Entropy'] = entropy(dist['probs'])
                    
                    
                    i=i+1
        else:
            continue
    
    df = pd.DataFrame.from_dict(data, orient='index').sort_index()
    df['Protocol'] = df['Protocol'].astype('category')
    df['Task'] = df['Task'].astype('category')
    
    return df
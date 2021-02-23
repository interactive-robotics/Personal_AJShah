#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 16:06:51 2020

@author: ajshah
"""

import pandas as pd
from puns.SpecificationMDP import *
from formula_utils import *
from scipy.stats import entropy
import os
import dill

discard = set([1])
Path = 'C:/Users/AJShah/Google Drive/Remote Interactive Robot Training/TableSetup_SubjectData'



def read_experiment_data(Path, exclude_random = False):
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
                if exclude_random and Protocol == 'Random':
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
    return df
    df['Protocol'] = df['Protocol'].astype('category')
    df['Task'] = df['Task'].astype('category')
    
    return df


def read_sim_data(Path, exclude_random = False, task = 'Task 1'):
    
    filename = os.path.join(Path, 'paired_summary.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)
    
    protocols = ['Active', 'Random', 'Batch'] if not exclude_random else ['Active',
                'Batch']
    
    df_data = {}
    idx = 0
    
    for p in protocols:
       for d in data[p]['dists']:
           df_data[idx] = {}
           df_data[idx]['Protocol'] = p
           df_data[idx]['Task'] = task
           df_data[idx]['Similarity'] = compare_distribution(data['true_formulas'][0], d)
           df_data[idx]['Entropy'] = entropy(d['probs'])
           idx=idx+1
    
    df = pd.DataFrame.from_dict(df_data, orient='index')
    
    return df
    
    
    

def get_task_assignments():
    
    task1 = []
    for i in range(10):
        
        base = 3*(2*i+1)
        task1.extend([base-1, base, base+1])
    
    task1 = set(task1)
    
    task2 = []
    for i in range(10):
        j = i+1
        base = 6*j
        task2.extend([base-1, base, base+1])
    task2 = set(task2)
    
    return task1, task2

def read_distribution(subject_id, condition):
    dirname = f'subject_{subject_id}_{condition}'

    if condition == 'Batch':
        final_dist = 'dist_3.json'
    else:
        final_dist = 'dist_3.json'

    filename = os.path.join(Path, dirname, 'Distributions',final_dist)

    with open(filename, 'r') as file:
        dist = json.load(file)

    if condition == 'Batch':
        n_threats = 0
        n_waypoints = 5
        accessibility = [True]*n_waypoints
        TraceSlice = {}
        for i in range(n_threats):
            TraceSlice[f'T{i}'] = False
        for i in range(n_waypoints):
            TraceSlice[f'W{i}'] = False
            TraceSlice[f'P{i}'] = accessibility[i]

        ProgressedFormulas = [ProgressSingleTimeStep(formula, TraceSlice) for formula in dist['support']]
        dist['formulas'] = ProgressedFormulas
    else:
        dist['formulas'] = dist['support']
    return dist

def collect_dataset(exp_path, sim_path_suffix,  exclude_random = False):
    
    experiment_data = read_experiment_data(exp_path, exclude_random = exclude_random)
    experiment_data['Source'] = 'Experiment'
    
    sim_data = []
    for (path, suffix) in sim_path_suffix:
        sim_data.append(read_sim_data(path, exclude_random = exclude_random, task = suffix))
    
    sim_data = pd.concat(sim_data, axis=0)
    sim_data['Source'] = 'Simulation'
    
    data = pd.concat([experiment_data, sim_data], axis=0)
    
    return pd.DataFrame.reset_index(data, drop = True)
    
    

if __name__ == '__main__':
    
    
    exp_path = '/home/ajshah/Data/Experiment2Data'
    sim_path_suffix = []
    sim_path_suffix.append(('/home/ajshah/Results/Task1_Simulated','Task 1'))
    sim_path_suffix.append(('/home/ajshah/Results/Task2_Simulated','Task 2'))
    
    data = collect_dataset(exp_path, sim_path_suffix, exclude_random = True)
    
    
    
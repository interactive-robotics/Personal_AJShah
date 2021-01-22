# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 07:50:11 2020

@author: AJShah
"""

from formula_utils import *
import os
from scipy.stats import entropy
import pandas as pd
import json
from puns.SpecificationMDP import *
import seaborn as sns
from sns_defaults import rc

subject_id = list(range(19))
exclude = [0,5,8,13]
discard = [1]
subject_id = [a  for a in subject_id if a not in exclude]
task1_formula = ['and',['F',['W0']],['F',['W1']],['F',['W2']],['F',['W3']],['F',['W4']],['U',['not',['W2']],['W1']],['U',['not',['W2']],['W0']],['U',['not',['W1']],['W0']]]
task2_formula = ['and',['G',['not',['W1']]],['F',['W0']],['F',['W2']],['U',['not',['W2']],['W0']]]
exp1_results_path = 'F:\TableSetup_SubjectData'
exp2_results_path = 'C:/Users/AJShah/Google Drive/Remote Interactive Robot Training/TableSetup_SubjectData'

def read_dist(dist_id, subj_id, protocol, path = exp1_results_path):
    
    dist_dir = os.path.join(path,f'subject_{subj_id}_{protocol}','Distributions')
    filename = os.path.join(dist_dir, f'dist_{dist_id}.json')
    
    with open(filename, 'r') as file:
        dist = json.load(file)
        
    if protocol == 'Batch' or (protocol == 'Active' and dist_id == 0):
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

def create_exp2_dataset():
    
    folders = os.listdir(exp2_results_path)
    task1, task2 = get_task_assignments()
    data = {}
    idx = 0
    
    for folder in folders:
        
        if folder.split('_')[0]=='subject':
            
            subj_id = int(folder.split('_')[1])
            protocol = folder.split('_')[2]
            task = 'Task 1' if subj_id in task1 else 'Task 2'
            
            if protocol in ['Batch', 'Active'] and subj_id not in discard:
                
                for dist_id in range(4):
                    
                    data[idx] = {}
                    data[idx]['subject ID'] = subj_id
                    data[idx]['Protocol'] = protocol
                    data[idx]['Trajectories'] = dist_id + 2
                    dist =  read_dist(dist_id, subj_id, protocol, path = exp2_results_path)
                    true_formula = task1_formula if subj_id in task1 else task2_formula
                    map_idx = np.argmax(dist['probs'])
                    data[idx]['MAP Similarity'] = compare_formulas(true_formula, dist['formulas'][map_idx])
                    data[idx]['Similarity'] = compare_distribution(true_formula, dist)
                    data[idx]['Entropy'] = entropy(dist['probs'])
                    data[idx]['Task'] = task
                    idx = idx + 1
                    
    df = pd.DataFrame.from_dict(data, orient='index').sort_index()
    df['Protocol'] = df['Protocol'].astype('category')
    df['Task'] = df['Task'].astype('category')
    return df
        
        
        

def create_exp1_dataset(subjects):
    
    data = {}
    idx = 0
    
    for subject in subjects:
        for protocol in ['Active','Batch']:
            for dist_id in range(4):
            
                data[idx] = {}
                data[idx]['subject ID'] = subject
                data[idx]['Protocol'] = protocol
                data[idx]['Trajectories'] = dist_id + 2
                dist = read_dist(dist_id, subject, protocol)
                data[idx]['Similarity'] = compare_distribution(task1_formula, dist)
                map_idx = np.argmax(dist['probs'])
                data[idx]['MAP Similarity'] = compare_formulas(task1_formula, dist['formulas'][map_idx])
                data[idx]['Entropy'] = entropy(dist['probs'])
                data[idx]['Task'] = 'Task 1'
                idx = idx + 1
    
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Protocol'] = df['Protocol'].astype('category')
    df['Task'] = df['Task'].astype('category')
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

if __name__ == '__main__':
    exp1 = create_exp1_dataset(subject_id)
    exp2 = create_exp2_dataset()
    full_data = pd.concat([exp1, exp2], axis=0)
    
    
    task1_data = full_data.loc[full_data['Task'] == 'Task 1']
    task2_data = full_data.loc[full_data['Task'] == 'Task 2']
    
    Active_data = full_data.loc[full_data['Protocol'] == 'Active']
    task1_data = Active_data.loc[Active_data['Task'] == 'Task 1']
    task2_data = Active_data.loc[Active_data['Task'] == 'Task 2']
    
    
    estimator = np.median
    
    with sns.plotting_context('poster',rc = rc):
        with sns.color_palette('dark'):
            plt.figure(figsize=[12,9])
            sns.lineplot(x = 'Trajectories',y = 'Similarity', hue = 'Task', data = Active_data, err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)
            plt.xlabel('Number of Task Executions')
            plt.xticks([2,3,4,5])
            plt.title('Median Similarity')
            plt.savefig('Exp_Similarity.png', dpi = 500, bbox_inches = 'tight')
            plt.savefig('Exp_Similarity.pdf', dpi = 500, bbox_inches = 'tight')
            
    
    
    with sns.plotting_context('poster',rc = rc):
        with sns.color_palette('dark'):
            plt.figure(figsize=[12,9])
            sns.lineplot(x = 'Trajectories',y = 'Entropy', hue = 'Task', data = Active_data, err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
            plt.xlabel('Number of Task Executions')
            plt.xticks([2,3,4,5])
            plt.title('Average Entropy')
            plt.savefig('Exp_Entropy.png', dpi = 500, bbox_inches = 'tight')
            plt.savefig('Exp_Entropy.pdf', dpi = 500, bbox_inches = 'tight')
    
    
    
    # with sns.plotting_context('poster',rc = rc):
    #     with sns.color_palette('dark'):
    #         plt.figure(figsize=[12,9])
    #         sns.lineplot(x = 'Trajectories',y = 'Similarity', hue = 'Protocol', data = task1_data, estimator = estimator)
    #         plt.xticks([2,3,4,5])
    
    
    
    # with sns.plotting_context('poster',rc = rc):
    #     with sns.color_palette('dark'):
    #         plt.figure(figsize=[12,9])
    #         sns.lineplot(x = 'Trajectories',y = 'Similarity', hue = 'Protocol', data = task2_data, estimator = estimator)
    #         plt.xticks([2,3,4,5])
    
    # with sns.plotting_context('poster',rc = rc):
    #     with sns.color_palette('dark'):
    #         plt.figure(figsize=[12,9])
    #         sns.lineplot(x = 'Trajectories',y = 'Similarity', hue = 'Protocol', data = task2_data, estimator = estimator)
    #         plt.xticks([2,3,4,5])
    
        
        
    import bootstrapped.bootstrap as bs
    task1_final = task1_data.loc[task1_data['Trajectories'] == 5]
    task2_final = task2_data.loc[task2_data['Trajectories'] == 5]
    final = Active_data.loc[Active_data['Trajectories'] == 5]
    
    import bootstrapped.stats_functions as bs_stats
    
    print('Task 1 Similarity:')
    print(bs.bootstrap(np.array(task1_final['Similarity']), bs_stats.median, is_pivotal=False))
    
    print('Task 2 Similarity:')
    print(bs.bootstrap(np.array(task2_final['Similarity']), bs_stats.median, is_pivotal=False))
    
    print('Overall Similarity:')
    print(bs.bootstrap(np.array(final['Similarity']), bs_stats.median, is_pivotal=False))
    
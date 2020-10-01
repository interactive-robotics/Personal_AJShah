# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:31:51 2020

@author: AJShah
"""

import os
os.environ['R_HOME'] = 'C:\Program Files\R\R-3.6.3'
os.environ['R_USER'] = 'C:/Users/AJShah/anaconda3/Lib/site-packages/rpy2'

from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, Formula
import pandas as pd
#from AutoEvalAnalysis import *
from puns.SpecificationMDP import *
from scipy.stats import entropy
import itertools
# from puns.utils import CreateSmallDinnerMDP
# from puns.ControlMDP import SmallTableMDP
# from puns.SpecificationMDP import *

pandas2ri.activate()
ARTool = importr('ARTool')
Path = 'C:/Users/AJShah/Google Drive/Remote Interactive Robot Training/TableSetup_SubjectData'

task1_formula = ['and',['F',['W0']],['F',['W1']],['F',['W2']],['F',['W3']],['F',['W4']],['U',['not',['W2']],['W1']],['U',['not',['W2']],['W0']],['U',['not',['W1']],['W0']]]
task2_formula = ['and',['G',['not',['W1']]],['F',['W0']],['F',['W2']],['U',['not',['W2']],['W0']]]
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

discard = set([1])

def read_dataset(exclude_batch = False):
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
    
        

def art_df(df:pd.DataFrame, formula:ro.Formula):
    
    #Perform the aligned rank transform on the dataframe
    m = ARTool.art(formula, data=df)
    
    #Perform ANOVA on the resulting data
    return ARTool.anova_art(m)

'''Formula Utils'''
def waypoints_and_orders(formula):
    #assume that formula is in ['and',....] format
    waypoints = []
    orders = []
    threats = []

    if formula[0] == 'and':
        subformulas = formula[1::]
    else:
        subformulas = [formula]

    for sub_formula in subformulas:
        if sub_formula[0] == 'F':
            waypoints.append(sub_formula[1][0])
        elif sub_formula[0]=='U':
            w1 = sub_formula[2][0]
            w2 = sub_formula[1][1][0]
            orders.append((w1,w2))
            waypoints.append(w1)
        elif sub_formula[0] == 'G':
            threats.append('G' + sub_formula[1][1][0])
        else:
            waypoints.append(0)

        #Remove the orders whose precedents are in Globals

        for order in orders:
            if 'G' + order[1] in threats:
                orders.remove(order)

    return waypoints, orders, threats

def compare_formulas(formula_1, formula_2):

    # Assume that they are in ['and' ...] format
    waypoints1, orders1, globals1 = waypoints_and_orders(formula_1)
    waypoints2, orders2, globals2 = waypoints_and_orders(formula_2)

    clauses_1 = set(waypoints1 + orders1 + globals1)
    clauses_2 = set(waypoints2 + orders2 + globals2)
    try:
        L = len(set.intersection(clauses_1,clauses_2))/len(set.union(clauses_1,clauses_2))
    except:
           print(clauses_1, clauses_2)
           print(formula_1, formula_2)
           L = 0
    return L

def compare_distribution(true_formula, distribution):
    similarities = [compare_formulas(true_formula, form) for form in distribution['formulas']]
    return np.dot(similarities, distribution['probs'])

def read_distribution(subject_id, condition):
    dirname = f'subject_{subject_id}_{condition}'

    if condition == 'Batch':
        final_dist = 'dist_0.json'
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

if __name__ == '__main__':
    
    data = read_dataset(exclude_batch=True)
    formula = Formula('Similarity ~ Protocol + Task + Protocol*Task')
    m = ARTool.art(formula, data)
    
    Tasks = ['Task 1', 'Task 2']
    Protocol = ['Active','Random','Batch']
    
    Similarities = {}
    mean_similarities = {}
    median_similarities = {}
    
    for (t,p) in itertools.product(Tasks, Protocol):
        Similarities[(t,p)] = data.loc[(data['Task'] == t) & (data['Protocol'] == p), 'Similarity']
        mean_similarities[(t,p)] = np.mean(Similarities[(t,p)])
        median_similarities[(t,p)] = np.median(Similarities[(t,p)])

    



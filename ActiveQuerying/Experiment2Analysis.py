# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:31:51 2020

@author: AJShah
"""

import os
os.environ['R_HOME'] = r"C:\Program Files\R\R-3.6.3"
os.environ['R_USER'] = 'C:/Users/AJShah/anaconda3/Lib/site-packages/rpy2'
os.environ['R_LIB'] = 'C:/Users/AJShah/Documents/R/win-library'
os.environ["PATH"]   = r"C:\Program Files\R\R-3.6.3\bin\x64" + ";" + os.environ["PATH"]

from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, Formula
import pandas as pd
#from AutoEvalAnalysis import *
from puns.SpecificationMDP import *
from scipy.stats import entropy
import itertools
from data_utils import *
from formula_utils import *
import dill
# from puns.utils import CreateSmallDinnerMDP
# from puns.ControlMDP import SmallTableMDP
# from puns.SpecificationMDP import *

pandas2ri.activate()
ARTool = importr('ARTool')

#Path = '/home/ajshah/Data/Experiment2Data'

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

if __name__ == '__main__':
    
    
    ''' Uncomment this for non-parametric ANOVA'''
    # data = read_dataset(exclude_batch=True)
    # formula = Formula('Similarity ~ Protocol + Task + Protocol*Task')
    # m = ARTool.art(formula, data)
    
    # Tasks = ['Task 1', 'Task 2']
    # Protocol = ['Active','Random','Batch']
    
    # Similarities = {}
    # mean_similarities = {}
    # median_similarities = {}
    
    # print(ARTool.anova_art(m))
    
    # for (t,p) in itertools.product(Tasks, Protocol):
    #     Similarities[(t,p)] = data.loc[(data['Task'] == t) & (data['Protocol'] == p), 'Similarity']
    #     mean_similarities[(t,p)] = np.mean(Similarities[(t,p)])
    #     median_similarities[(t,p)] = np.median(Similarities[(t,p)])
    
    '''Uncomment this for a runthrough of Subj 23'''
    from data_utils import Path
    subj_id = 23
    subj_dir = os.path.join(Path, f'subject_{subj_id}_Active')
    log_dir = os.path.join(subj_dir, 'logs')
    
    with open(os.path.join(log_dir, 'query_0.pkl'), 'rb') as file:
        query1 = dill.load(file)



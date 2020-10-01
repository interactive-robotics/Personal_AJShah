#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 13:40:41 2020

@author: ajshah
"""

from AutoEvalAnalysis import *
from puns.utils import CreateSmallDinnerMDP
from puns.ControlMDP import SmallTableMDP
from puns.SpecificationMDP import *
import json
import os
from scipy.stats import entropy
import pandas as pd
import pingouin as pg

results_path = '/home/ajshah/TableSetup_SubjectData'

true_formula = ['and']
for i in range(5):
    true_formula.append(Eventually(f'W{i}'))

true_formula.append(Order('W0','W1'))
true_formula.append(Order('W0','W2'))
true_formula.append(Order('W1','W2'))

objects = {}
objects[0] = 'DinnerPlate'
objects[1] = 'SmallPlate'
objects[2] = 'Bowl'
objects[3] = 'Knife'
objects[4] = 'Fork'


def read_distribution(subject_id, condition):
    dirname = f'subject_{subject_id}_{condition}'

    if condition == 'Batch':
        final_dist = 'dist_0.json'
    else:
        final_dist = 'dist_3.json'

    filename = os.path.join(results_path, dirname, 'Distributions',final_dist)

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

def create_entry(subject_id, condition):

    entry = {}
    dist = read_distribution(subject_id, condition)
    entry['Entropy'] = entropy(dist['probs'])
    entry['Similarity'] = compare_distribution(true_formula, dist)
    entry['subject_id'] = subject_id
    entry['Protocol'] = condition
    map_formula = dist['formulas'][np.argmax(dist['probs'])]
    entry['map'] = map_formula
    entry['map_similarity'] = compare_formulas(map_formula, true_formula)

    return entry

def subject_metrics(subject_id):
    data = {}
    i=0
    for cond in ['Active','Random','Batch']:
        data[i] = create_entry(subject_id, cond)
        i=i+1
    return data

def collect_data(subj_ids, exclude):
    included = list(set(subj_ids) - set(exclude))

    data = {}
    i = 0
    for idx in included:
        for condition in ['Active','Batch','Random']:
            data[i] = create_entry(idx, condition)
            i=i+1
    return pd.DataFrame.from_dict(data, orient = 'index')

def parse_demonstration(subject_id, condition = 'Active', demo_id = 0):
    dirname = f'subject_{subject_id}_{condition}'
    demofile = f'demos/demo_{demo_id}.txt'

    filename = os.path.join(results_path, dirname, demofile)
    with open(filename,'r') as file:
        lines = file.readlines()

    state_tuples = [tuple(json.loads(line)) for line in lines]
    cmdp = SmallTableMDP()
    trace_slices = [cmdp.create_observations(t) for t in state_tuples]

    placed = [False]*5
    order = []
    for i in range(len(trace_slices)-1):

        for j in range(5):
            if trace_slices[i][f'W{j}'] == False and trace_slices[i+1][f'W{j}'] == True and placed[j] == False:
                placed[j] = True
                order.append(j)

    return tuple(order)

def collect_orders(subj, exclude, condition = 'Batch'):

    if condition == 'Batch':
        n_demo = 5
    else:
        n_demo = 2
    orders = {}

    included = list(set(subj) - set(exclude))

    for idx in included:

        orders[idx] = []
        for k in range(n_demo):
            orders[idx].append(parse_demonstration(idx, condition=condition, demo_id = k))
    return orders

def collect_robot_orders(subj, exclude, condition = None):
    if condition == None:
        condition = ['Active','Random','Batch']
    else:
        condition = [condition]

    #for c in condition:


def collect(data, label='Experiment'):
    final_data = {}
    i = 0

    for row in data.iterrows():
            final_data[i] = {}
            final_data[i]['Similarity'] = row[1]['Similarity']
            final_data[i]['Entropy'] = row[1]['Entropy']
            final_data[i]['Protocol'] = row[1]['Protocol']
            final_data[i]['Type'] = label
            i=i+1
    return pd.DataFrame.from_dict(final_data, orient = 'index')

def read_subjective_data(subjects, excluded):

    included = list(set(subjects) - set(excluded))

    data = pd.read_csv('ExperimentData.csv')
    filtered_data = data.loc[data['Participant ID'].isin(included)]
    filtered_data = filtered_data[['Participant ID', 'Task ID' ,'Q1','Q2','Q3','Q4','Q5','Overall']]
    return filtered_data

def cronbach_alpha(items):
    items = pd.DataFrame(items)
    items_count = items.shape[1]
    variance_sum = float(items.var(axis=0, ddof=1).sum())
    total_var = float(items.sum(axis=1).var(ddof=1))

    return (items_count / float(items_count - 1) *
            (1 - variance_sum / total_var))



if __name__ == '__main__':

    subj = list(range(1,19))
    exclude = [5,8,13]
    data = collect_data(subj, exclude)
    orders = collect_orders(subj, exclude)

    sim_data = pd.DataFrame()

    for i in [3]:
        params.n_queries = i
        n = params.n_queries + params.n_demo
        params.results_path = f'/home/ajshah/Results/TableSetup_{n}_with_baseline'

        new_data = assimilate_metrics(['Active','Random','Batch'])
        sim_data = pd.concat([sim_data, new_data])
        sim_data.reindex()
        Entropy = report_entropies(['Active','Random','Batch'])
        #plot_entropy(Entropy)
        Similarity = report_similarities(['Active','Random','Batch'])
        #plot_similarity(Similarity)
    sim_data['Protocol'] = sim_data['type']
    new_data1 = collect(sim_data, 'Simulated')
    new_data2 = collect(data,'Experiment')

    new_data = pd.concat([new_data1, new_data2], ignore_index='True')

    #Plotting
    bar_plots(new_data)



    #Friedman test of significant difference
    print('Friedman test for Similarity')
    friedman_similarity = pg.friedman(data = data, dv = 'Similarity', within='Protocol', subject='subject_id')
    print(friedman_similarity, '\n\n')


    Active = data.loc[data['Protocol']=='Active']['Similarity']
    Batch = data.loc[data['Protocol']=='Batch']['Similarity']
    Random = data.loc[data['Protocol']=='Random']['Similarity']

    EActive = data.loc[data['Protocol']=='Active']['Entropy']
    EBatch = data.loc[data['Protocol'] == 'Batch']['Entropy']
    ERandom = data.loc[data['Protocol'] == 'Random']['Entropy']

    #Wilcoxon Active Batch
    print('WRS test for Active - Batch')
    print(pg.wilcoxon(Active, Batch, tail='one-sided'), '\n\n')

    #Mann Whitney Active Batch
    print('Mann Whitney U test for Active, Batch')
    print(pg.mwu(Active, Batch, tail='one-sided'),'\n\n')

    #Wilcoxon Batch Random
    print('WRS test for Batch - Random')
    print(pg.wilcoxon(Batch, Random, tail='one-sided'), '\n\n')

    print('Mann Whitney U test for Batch - Random')
    print(pg.mwu(Batch, Random, tail='one-sided'), '\n\n')

    #Wilcoxon Active Random
    print('WRS test for Active - Random')
    print(pg.wilcoxon(Active, Random, tail='one-sided'), '\n\n')

    print('Mann Whitney U test for Active - Random')
    print(pg.mwu(Active, Random, tail='one-sided'), '\n\n')

    print('Friedman test for Entropy')
    friedman_similarity = pg.friedman(data = data, dv = 'Entropy', within='Protocol', subject='subject_id')
    print(friedman_similarity, '\n\n')

     #Wilcoxon Active Batch
    print('WRS test for Active - Batch')
    print(pg.wilcoxon(EActive, EBatch, tail='one-sided'), '\n\n')


    print('WRS test for Active - Random')
    print(pg.wilcoxon(EActive, ERandom, tail='one-sided'), '\n\n')

    print('WRS test for Batch - Random')
    print(pg.wilcoxon(EBatch, ERandom, tail='one-sided'), '\n\n')


    subjective_data = read_subjective_data(subj, exclude)
    subjective_data['Q4'] = 6 - subjective_data['Q4']

    A = subjective_data.loc[subjective_data['Task ID']=='A']
    B = subjective_data.loc[subjective_data['Task ID']=='B']
    C = subjective_data.loc[subjective_data['Task ID']=='C']

    print('Friedman test for overall rating')
    print(pg.friedman(data = subjective_data, dv = 'Overall', within = 'Task ID', subject = 'Participant ID'))

    print('\n\nReliability Analysis')
    print('Q1,2,3:')
    a = cronbach_alpha([subjective_data['Q1'].tolist(), subjective_data['Q2'].tolist(), subjective_data['Q3'].tolist()])
    print('Alpha: ', a)

    print('\n\n')
    print('Q4,5')
    a2 = cronbach_alpha([subjective_data['Q4'].tolist() , subjective_data['Q5'].tolist()])
    print('Alpha: ', a2)

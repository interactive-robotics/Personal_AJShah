# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 15:47:37 2021

@author: AJShah
"""

from pedagogical_demo import *
from query_selection import *
from Auto_Eval_Active import *
from tqdm import tqdm
from itertools import product
from multiprocessing import Pool
import seaborn as sns
import os
import dill

directory =  'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def determine_mismatch(dist, strat1, strat2):

    retval = {}
    spec_fsm = SpecificationFSM(dist['formulas'], dist['probs'])

    s1 = identify_desired_state(spec_fsm, query_type = strat1)
    s2 = identify_desired_state(spec_fsm, query_type = strat2)

    if s1[0] != s2[0]:
        retval['flag'] = True
        if s1[0] != spec_fsm.id2states[0] and s2[0] != spec_fsm.id2states[0]:
            retval['trivial'] = False

    return retval

def find_query_mismatches_parallel(d, strat1, strat2):

    conditions = list(set(d['results'][0].keys()) - set(['ground_truth']))
    n_queries = len(d['results'][0][conditions[0]])
    dists = [d['results'][i][c][q] for (i,c,q) in product(d['results'].keys(), conditions, range(n_queries))]
    
    ret = []
    
    for batch in tqdm(list(chunks(dists,8))):
        with Pool(processes = len(batch)) as pool:
            retvals = pool.starmap(determine_mismatch, zip(batch, len(batch)*[strat1], len(batch)*[strat2]))
        ret.append(retvals)
    return ret, dists


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
                    if s1[0] != spec_fsm.id2states[0] and s2[0] != spec_fsm.id2states[0]:
                        diverging_dists[-1]['trivial'] = False
                    else:
                        diverging_dists[-1]['trivial'] = True

    return diverging_dists

def get_selections(dat, format = 'long'):
    selections = dat['meta_selections']
    
    if format == 'long':
        out_data = {}
        idx = 0
        for  i in selections.keys():
            for c in selections[i].keys():
                for q in range(len(selections[i][c])):
                    out_data[idx] = {}
                    out_data[idx]['Condition'] = c
                    out_data[idx]['Query'] = q
                    out_data[idx]['Selection'] = selections[i][c][q]
                    idx = idx+1
        out_data = pd.DataFrame.from_dict(out_data, orient = 'index')
        return out_data
    
    if format == 'condition':
        out_data = {}
        idx = 0
        
        for c in selections[0].keys():
            out_data[c] = {}
            for i in selections.keys():
                out_data[c][i] = {}
                for q in range(len(selections[i][c])):
                    out_data[c][i][q] = selections[i][c][q]
            
            out_data[c] = pd.DataFrame.from_dict(out_data[c], orient = 'index')
        return out_data
        
                    
def plot_selections(data):
    
    selections = get_selections(data, format = 'condition')
    
    for c in selections.keys():
         raw_frame = selections[c]
         index = raw_frame.columns
         query_counts = [raw_frame[x].value_counts()['query'] if 'query' in raw_frame[x].value_counts().index else 0 for x in index]
         demo_counts = [raw_frame[x].value_counts()['demo'] if 'demo' in raw_frame[x].value_counts().index else 0 for x in index]
         
         plot_frame = pd.DataFrame({'Queries': query_counts, 'Demonstrations': demo_counts}, index = index)
         from sns_defaults import rc
         with sns.plotting_context('poster', rc = rc):
             plt.figure(figsize = [16, 9])
             plot_frame.plot.bar(stacked = True, ax = plt.gca())
             plt.title(f'{c}')



if __name__ == '__main__':

    print('Reading Results file \n')
    with open(os.path.join(directory, 'meta_summary.pkl'),'rb') as file:
        d = dill.load(file)

    #ret, dists = find_query_mismatches_parallel(d, 'uncertainty_sampling', 'max_model_change')
    #dists = find_query_mismatches(d, 'uncertainty_sampling', 'max_model_change')
    #data = get_selections(d, format = 'condition')
    plot_selections(d)
    

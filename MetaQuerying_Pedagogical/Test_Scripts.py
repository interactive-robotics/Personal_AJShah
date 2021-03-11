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



if __name__ == '__main__':

    print('Reading Results file \n')
    with open(os.path.join(directory, 'active_paired_summary.pkl'),'rb') as file:
        d = dill.load(file)

    #ret, dists = find_query_mismatches_parallel(d, 'uncertainty_sampling', 'max_model_change')
    dists = find_query_mismatches(d, 'uncertainty_sampling', 'max_model_change')

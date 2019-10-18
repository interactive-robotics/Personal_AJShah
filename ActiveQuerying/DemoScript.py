#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 11:50:47 2019

@author: ajshah
"""

import json
from os import listdir
import os
import pandas as pd
import numpy as np
import active_params as params
import networkx as nx
from copy import deepcopy
import matplotlib.pyplot as plt
from functools import reduce
from puns.utils import CreateSpecMDP
from puns.SpecificationMDP import *
from puns.LearningAgents import QLearningAgent
from puns.Exploration import ExplorerAgent

def plot_probs(MDP, show_cdf = False):
    Probs = MDP.specification_fsm._partial_rewards
    plt.bar(range(len(Probs)), np.sort(Probs)[::-1])
    if show_cdf:
        f = lambda i: reduce( lambda memo, x: memo+x, np.flip(np.sort(Probs),0)[0:i+1], 0)
        plt.plot(range(len(Probs)), list(map(f, range(len(Probs)))))


def read_raw_data(dir):
    filenames = listdir(dir)
    Trajs = []
    for filename in filenames:
        Trajs.append(json.load(open(os.path.join(dir, filename),'r')))
    return Trajs

def write_data(dir, data):
    for (i, traj) in enumerate(data):
        json.dump(traj, open(os.path.join(dir, f'Predicates_{i}.json'),'w'))

def compress_data(raw_data):
    compressed_data = []
    for traj in raw_data:
        compressed_traj = compress_traj((traj))
        new_data = {}
        new_data['Data'] = compressed_traj
        new_data['Label'] = True
        compressed_data.append(new_data)
    return compressed_data

def compress_traj(traj):
    n_waypoints = len(traj['WaypointPredicates'])
    n_positions = n_waypoints
    n_threats = len(traj['ThreatPredicates']) if 'ThreatPredicates' in traj.keys() else 0

    df1 = np.array(traj['WaypointPredicates']).transpose()
    df2 = np.array(traj['PositionPredicates']).transpose()


    if n_threats > 0:

        df3 = np.array(traj['ThreatPredicates']).transpose()
        datamatrix = np.concatenate([df1, df2, df3], axis = 1)
    else:
        datamatrix = np.concatenate([df1, df2], axis = 1)


    dataframe = pd.DataFrame(datamatrix)
    dataframe.drop_duplicates(inplace = True)
    compressed_datamatrix = np.array(dataframe)

    compressed_waypoints = compressed_datamatrix[:,0:n_waypoints].transpose().tolist()
    compressed_positions = compressed_datamatrix[:, n_waypoints : n_waypoints + n_positions].transpose().tolist()

    compressed_traj = {}
    compressed_traj['WaypointPredicates'] = compressed_waypoints
    compressed_traj['PositionPredicates'] = compressed_positions
    if n_threats > 0:
        compressed_traj['ThreatPredicates'] = compressed_datamatrix[:,-n_threats:].transpose().tolist()

    return compressed_traj

def sort_formulas(formulas, probs):
    idx = np.argsort(probs)[::-1]
    probs = np.array(probs)[idx]
    sorted_formulas = np.empty((len(idx),), dtype=object)
    for i in range(len(idx)):
        sorted_formulas[i] = formulas[idx[i]]
    formulas = sorted_formulas
    return sorted_formulas, probs

def identify_desired_state(specification_fsm:SpecificationFSM, non_terminal=True):
    if non_terminal:
        states = list(specification_fsm.states2id.keys())
        rewards = [specification_fsm.reward_function(state, force_terminal=True) for state in states]
    else:
        states = specification_fsm.terminal_states
        rewards = [specification_fsm.reward_function(state) for state in specification_fsm.terminal_states]

    desired_state = states[np.argmin(np.abs(rewards))]
    path_to_desired_state = nx.all_simple_paths(specification_fsm.graph, 0, specification_fsm.states2id[desired_state])
    bread_crumb_states = set([l for sublists in path_to_desired_state for l in sublists]) - set([specification_fsm.states2id[desired_state]])
    return desired_state, bread_crumb_states

def identify_desired_state_non_terminal(specification_fsm:SpecificationFSM):
    states = list(specification_fsm.states2id.keys())
    rewards = [specification_fsm.reward_function(state, force_terminal=True) for state in states]
    desired_state = states[np.argmin(np.abs(rewards))]
    path_to_desired_state = nx.all_simple_paths(specification_fsm.graph, 0, specification_fsm.states2id[desired_state])
    bread_crumb_states = set([l for sublists in path_to_desired_state for l in sublists]) - set([specification_fsm.states2id[desired_state]])
    return desired_state, bread_crumb_states

def recompile_reward_function(specification_fsm:SpecificationFSM, desired_state, breadcrumb_states):
    spec_fsm2 = deepcopy(specification_fsm)

    def Reward(state, prev_state = None, force_terminal=False):

        if force_terminal:
            if state == desired_state:
                return 1
            else:
                return -1
        else:
            if state == desired_state:
                return 1
            elif spec_fsm2.states2id[state] in breadcrumb_states:
                return 0
            else:
                return -1

    spec_fsm2.reward_function = Reward
    return spec_fsm2

def modify_formula(formula):
    if formula[0] == 'and':
        conjuncts = deepcopy(formula[1::])
    else:
        conjuncts = [deepcopy(formula)]

    if len(conjuncts) > 1:
        #Remove an element
        remove_element = np.random.randint(len(conjuncts))
        conjuncts.remove(conjuncts[remove_element])

        #And it back to a conjunctive formula
        if len(conjuncts) > 1:
            modified_formula = ['and']
            modified_formula.extend(conjuncts)
        else:
            modified_formula = conjuncts[0]
    else:
        modified_formula = [True]

    return modified_formula

def create_baseline_query(MDP, verbose = True):
    '''Creates a query by randomly removing a conjunctive clause from the MAP
    formula'''

    specification_fsm = MDP.specification_fsm
    control_mdp = deepcopy(MDP.control_mdp)

    map_formula = specification_fsm._formulas[0]
    modified_formula = modify_formula(map_formula)

    if modified_formula != [True]:
        spec_fsm2 = SpecificationFSM(formulas = [modified_formula], probs = [1])
        MDP2 = SpecificationMDP(spec_fsm2, control_mdp)
        agent = QLearningAgent(MDP2)
        agent.explore(episode_limit=5000, action_limit = 100000, verbose = verbose)

        eval_agent = ExplorerAgent(MDP2, input_policy = agent.create_learned_softmax_policy(0.001))
        eval_agent.explore(episode_limit = 1)

        #Create the proposition trace_slices
        episode_record = eval_agent.episodic_record[0]
        trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
        trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))

        return {'trace': trace_slices, 'agent': eval_agent, 'modified_formula': modified_formula}
    else:
        query = create_random_query(MDP, verbose=True)
        query['modified_formula'] = [True]
        return query



def create_random_query(MDP, verbose=True):

    ''' Creates a randomly generated query obtained by randomly sampling
    control MDP actions till a terminal state is reached'''

    #Generate a random demonstration
    MDP2 = deepcopy(MDP)
    random_agent = ExplorerAgent(MDP2)
    random_agent.explore(episode_limit = 1)
    #_ = random_agent.visualize_exploration()

    # Create the proposition trace for the generated demonstration
    episode_record = random_agent.episodic_record[0]
    trace_slices = [MDP2.control_mdp.create_observations(record[0][1]) for record in episode_record]
    trace_slices.append(MDP2.control_mdp.create_observations(episode_record[-1][2][1]))

    return {'trace': trace_slices, 'agent': random_agent}

def create_active_query_non_terminal(MDP, verbose = True):
    ''' A query generated as per the most informative heuristic based on the
    identified final state

    NOW DEPRECATED: use create_active_query(MDP, non_terminal=True) instead'''

    # Identify desired final state and recompile reward
    desired_state, breadcrumbs = identify_desired_state_non_terminal(MDP.specification_fsm)
    spec_fsm2 = recompile_reward_function(MDP.specification_fsm, desired_state, breadcrumbs)
    spec_fsm2.terminal_states.append(desired_state)

    # Re-define MDP and learning agent
    MDP2 = SpecificationMDP(spec_fsm2, MDP.control_mdp)
    agent = QLearningAgent(MDP2)

    # Train learning agent to produce a query
    agent.explore(episode_limit = 5000, action_limit = 1000000, verbose = verbose)
    eval_agent = ExplorerAgent(MDP2, input_policy = agent.create_learned_softmax_policy(0.001))

    # Generate a query with the trained agent and visualize query
    eval_agent.explore(episode_limit = 1)
    #_ = eval_agent.visualize_exploration()

    # Create proposition trace slices
    episode_record = eval_agent.episodic_record[0]
    trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
    trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))

    return {'trace': trace_slices, 'agent': eval_agent, 'desired_state': desired_state}

def create_active_query(MDP, verbose = True, non_terminal=True):
    ''' A query generated as per the most informative heuristic based on the
    identified final state'''

    # Identify desired final state and recompile reward
    desired_state, breadcrumbs = identify_desired_state(MDP.specification_fsm, non_terminal)
    spec_fsm2 = recompile_reward_function(MDP.specification_fsm, desired_state, breadcrumbs)
    if non_terminal:
        spec_fsm2.terminal_states.append(desired_state)

    # Re-define MDP and learning agent
    MDP2 = SpecificationMDP(spec_fsm2, MDP.control_mdp)
    agent = QLearningAgent(MDP2)

    # Train learning agent to produce a query
    agent.explore(episode_limit = 5000, action_limit = 1000000, verbose = verbose)
    eval_agent = ExplorerAgent(MDP2, input_policy = agent.create_learned_softmax_policy(0.001))

    # Generate a query with the trained agent and visualize query
    eval_agent.explore(episode_limit = 1)
    #_ = eval_agent.visualize_exploration()

    # Create proposition trace slices
    episode_record = eval_agent.episodic_record[0]
    trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
    trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))

    return {'trace': trace_slices, 'agent': eval_agent, 'desired_state': desired_state}

def create_query_demo(trace_slices):
    ''' Reformats the generated demonstration into a form readable by the webppl
     active query code'''

    n_waypoints = len([k for k in trace_slices[0].keys() if 'W' in k])
    n_threats = len([k for k in trace_slices[0].keys() if 'T' in k])

    new_traj = {}
    new_traj['WaypointPredicates'] = []
    for i in range(n_waypoints):
        new_traj['WaypointPredicates'].append([k[f'W{i}'] for k in trace_slices])
    if n_threats > 0:
        new_traj['ThreatPredicates'] = []
        for i in range(n_threats):
            new_traj['ThreatPredicates'].append([k[f'T{i}'] for k in trace_slices])

    new_traj['PositionPredicates'] = []
    ScenarioLength = len(new_traj['WaypointPredicates'][0])
    for i in range(len(new_traj['WaypointPredicates'])):
        new_traj['PositionPredicates'].append(np.zeros((ScenarioLength)).astype(bool).tolist())
    return new_traj

def write_demo_query_data(new_traj, label, dir,  query_number = None, filename = 'query'):
    '''Write the demo query along with the user provided label'''

    if query_number == None:
        i = 1
        while os.path.exists(os.path.join(dir, f'{filename}_{i}.json')):
            i=i+1
        query_number = i

    filename = f'{filename}_{query_number}.json'

    new_data = {}
    new_data['Data'] = new_traj
    new_data['Label'] = label
    print(f'Writing file: {filename}')
    json.dump(new_data, open(os.path.join(dir, filename),'w'))

def create_signal(trace_slices):
    signal = {}
    signal['length'] = len(trace_slices)
    for key in trace_slices[0].keys():
        signal[key] = []
        for slice in trace_slices:
            signal[key].append(slice[key])
    return signal








if __name__ == '__main__':

    ''' Filter the trajectories while retaining only the time stamps with changes '''
    #Import the traj Data
    raw_data = read_raw_data(params.raw_data_path)

    #Compress data
    compressed_data = compress_data(raw_data)

    #Write the compressed data to file
    write_data(params.compressed_data_path, compressed_data)

    ''' Perform Specification inference on the compressed data '''
    inference_path = 'bsi_batch.js'
    print('Executing Bayesian Specification Inference')
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.nSamples}  --nBurn {params.nBurn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.output_path}\' --nTraj {params.nTraj}'
    returnval = os.system(infer_command)
    if returnval:
        Exception('Inference Error')

    '''Read specification and plot the formula probabilities'''
    specification = json.load(open(os.path.join(params.output_path, 'batch_posterior.json'),'r'))
    formulas = specification['support']
    probs = specification['probs']

    plt.bar(range(len(probs)), np.sort(probs)[::-1])
    f = lambda i: reduce( lambda memo, x: memo+x, np.flip(np.sort(probs),0)[0:i+1], 0)
    plt.plot(range(len(probs)), list(map(f, range(len(probs)))))

    ''' Compile an instance of PUNS and plan with 10000 training episode '''
    print('Compiling PUnS instance')
    MDP = CreateSpecMDP(os.path.join(params.output_path,'batch_posterior.json'), 0, 5)
    QAgent = QLearningAgent(MDP)
    print('Training PuNS instance')
    #QAgent.explore(episode_limit = 10000, action_limit = 100000, verbose=True)

    print('Evaluating trained agent')
    #eval_agent = ExplorerAgent(MDP, input_policy = QAgent.create_learned_softmax_policy(0.01))
    #eval_agent.explore(episode_limit=100)
    #col = eval_agent.visualize_exploration(prog='neato')

    print('Getting desired state for most informative query')
    desired_state, bread_crumb_states = identify_desired_state(MDP.specification_fsm)

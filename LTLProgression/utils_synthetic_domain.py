#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:41:54 2019

"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import pygraphviz as pgv
from utils import *
from LearningAgents import *

MDPCreator = {}
MDPCreator[1] = CreateSpecMDP1
MDPCreator[2] = CreateSpecMDP2
MDPCreator[3] = CreateSpecMDP3
MDPCreator[4] = CreateSpecMDP4


def TrainAndEvalMDP(IDx, key, risk_level = 0.3, prog='neato', print_terminal = False):
    MDPFunction = MDPCreator[IDx]
    MDP, fsm, cmdp = MDPFunction(reward_type = key, risk_level = risk_level)
    q_agent = QLearningAgent(MDP)
    q_agent.explore(episode_limit = 1000, verbose = False)
    stoch_eval = ExplorerAgent(MDP, input_policy=q_agent.create_learned_softmax_policy(0.02))
    stoch_eval.explore(episode_limit = 1000, verbose = False)
    print('\n')
    VisualizeExploration(stoch_eval, prog = prog)
    print('Size of the specification FSM: ', len(MDP.specification_fsm.states2id))
    print('Formulas considered: ', len(MDP.specification_fsm._formulas))
    
    r = [record[-1][3] for record in stoch_eval.episodic_record]
    if print_terminal:
        print('Average terminal reward: ', np.mean(r))
        print('Median terminal reward: ', np.median(r))
    return q_agent, stoch_eval, MDP


def LabelNode(node):
    cmdp_state = node[1]
    threats = cmdp_state[0]
    waypoints = cmdp_state[1::]
    label = 'S'
    if threats: 
        label = 'T0'
    else:
        for (i,val) in enumerate(waypoints):
            if val: label = f'W{i}'

    return label

def VisualizeExploration(Learner:ExplorerAgent, prog = 'neato'):
    G = Learner.G
    NodeLabels = {}
    for node in G.nodes:
        NodeLabels[node] = LabelNode(node)
        
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog = prog)
    nx.draw_networkx(G, pos, node_size = 12500, width = 2.5, with_labels = False, arrowsize=40)
    _ = nx.draw_networkx_labels(G, pos, NodeLabels, font_size = 32, font_color='w')
    plt.box(False)
    
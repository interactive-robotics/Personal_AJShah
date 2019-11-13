#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 18:48:37 2019

@author: ajshah
"""

import puns.Constants as Constants
from puns.SpecificationMDP import *
from puns.ControlMDP import *
from puns.Exploration import ExplorerAgent


def CreateSampleMDP():
    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    TraceSlice = GetTraceSlice(SampleSignal,0)
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas_synth = np.array(Formulas)[idx]
    Probs = np.array(Prob)[idx]
    ProgressedFormulas = np.array([ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas_synth])

    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type='min_regret', risk_level=0.3)
    control_mdp = SyntheticMDP(5,4)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP

def CreateSpecMDP(PathToSpec, n_threats, n_waypoints, accessibility=None, reward_type = 'min_regret', risk_level = 0.1):

    if accessibility == None: accessibility = [True]*n_waypoints

    control_mdp = SyntheticMDP(n_threats, n_waypoints, accessibility)

    Data = json.load(open(PathToSpec,'r'))
    Formulas = Data['support']
    Probs = Data['probs']
    import matplotlib.pyplot as plt
    # plt.bar(range(len(Probs)), np.sort(Probs)[::-1])
    # f = lambda i: reduce( lambda memo, x: memo+x, np.flip(np.sort(Probs),0)[0:i+1], 0)
    # plt.plot(range(len(Probs)), list(map(f, range(len(Probs)))))

    TraceSlice = {}
    for i in range(n_threats):
        TraceSlice[f'T{i}'] = False
    for i in range(n_waypoints):
        TraceSlice[f'W{i}'] = False
        TraceSlice[f'P{i}'] = accessibility[i]

    ProgressedFormulas = [ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas]
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type=reward_type, risk_level=risk_level)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP


def Globally(p):
    if type(p) == list:
        return ['G', p]
    else:
        return ['G',['not',[p]]]

def Eventually(p):
    return ['F',[p]]

def Order(p1, p2):
    return ['U',['not',[p2]],[p1]]

def CreateSpecMDP1(reward_type = 'min_regret', risk_level = '0.1'):
    control_mdp = SyntheticMDP(1,3)

    Formulas = []
    Formulas.append(['and', Globally('T0'), Eventually('W0'), Eventually('W1'), Eventually('W2'), Order('W0','W1'), Order('W0','W2'), Order('W1','W2')])
    Formulas.append(['and', Globally('T0'), Eventually('W0'), Eventually('W1'), Eventually('W2')])
    Formulas.append(['and', Globally('T0'), Eventually('W0')])

    Probs = [0.8, 0.15, 0.05]
    specification_fsm = SpecificationFSM(Formulas, Probs, reward_type = reward_type, risk_level=risk_level)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP, specification_fsm, control_mdp

def CreateSpecMDP2(reward_type = 'min_regret', risk_level = '0.1'):
    control_mdp = SyntheticMDP(1,3)

    Formulas = []
    Formulas.append(['and', Globally('T0'), Eventually('W0'), Eventually('W1'), Eventually('W2'), Order('W0','W1'), Order('W0','W2'), Order('W1','W2')])
    Formulas.append(['and', Globally('T0'), Eventually('W0'), Eventually('W1'), Eventually('W2')])
    Formulas.append(['and', Globally('T0'), Eventually('W0')])

    Probs = [0.05, 0.15, 0.8]
    specification_fsm = SpecificationFSM(Formulas, Probs, reward_type = reward_type, risk_level=risk_level)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP, specification_fsm, control_mdp

def CreateSpecMDP3(reward_type = 'min_regret', risk_level = '0.1'):
    control_mdp = SyntheticMDP(1,3)

    Formulas = []
    Formulas.append(['and', Globally('T0'), Eventually('W0')])
    Formulas.append(['and', Globally('T0'), Eventually('W1')])
    Formulas.append(['and', Globally('T0'), Eventually('W2')])

    Probs = [0.4, 0.25, 0.35]
    specification_fsm = SpecificationFSM(Formulas, Probs, reward_type = reward_type, risk_level=risk_level)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP, specification_fsm, control_mdp

def CreateSpecMDP4(reward_type = 'min_regret', risk_level = '0.1'):
    control_mdp = SyntheticMDP(1,3)

    Formulas = []
    Formulas.append(['and', Globally('T0'), Eventually('W0'), Globally(['not',['W2']])])
    Formulas.append(['and', Globally('T0'), Eventually('W1'), Globally(['not',['W2']])])
    Formulas.append(['and', Globally('T0'), Eventually('W2')])

    Probs = [0.05, 0.15, 0.8]
    specification_fsm = SpecificationFSM(Formulas, Probs, reward_type = reward_type, risk_level=risk_level)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP, specification_fsm, control_mdp

def CreateDinnerMDP(reward_type = 'min_regret', failure_prob = 0.2, num_steps = 1):

    control_mdp = TableMDP(failure_prob, num_steps)

    Data = json.load(open('DinnerTable_OutputDist_Sampler4_Custom_30.json','r'))
    Formulas, Probs = Data['support'],Data['probs']

    n_threats = 1
    n_waypoints = 8
    accessibility = [True]*n_waypoints
    TraceSlice = {}
    for i in range(n_threats):
        TraceSlice[f'T{i}'] = False
    for i in range(n_waypoints):
        TraceSlice[f'W{i}'] = False
        TraceSlice[f'P{i}'] = accessibility[i]

    ProgressedFormulas = [ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas]
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type = reward_type)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP

def CreateSmallDinnerMDP(specfile, reward_type = 'min_regret', failure_prob = 0.0, num_steps = 1):

    control_mdp = SmallTableMDP(failure_prob, num_steps)

    with open(specfile, 'r') as file:
        Data = json.load(file)
    Formulas, Probs = Data['support'],Data['probs']

    n_threats = 0
    n_waypoints = 5
    accessibility = [True]*n_waypoints
    TraceSlice = {}
    for i in range(n_threats):
        TraceSlice[f'T{i}'] = False
    for i in range(n_waypoints):
        TraceSlice[f'W{i}'] = False
        TraceSlice[f'P{i}'] = accessibility[i]

    ProgressedFormulas = [ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas]
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type = reward_type)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    return MDP


def RecordLearningCurve(MDP, Learner, max_episodes = 10000, steps = 10, temp = 0.01, verbose = False):
    episodes = 0
    mean_rewards = []
    rewards = []
    std_rewards = []
    mean_episode_length = []
    ep = []

    for i in range(0,max_episodes,steps):

        if verbose:
            print(f'\r Training and evaluating with {i} episodes        ', end = '')

        episodes = episodes + steps
        ep.append(episodes)
        Learner.explore(episode_limit = steps, verbose = False)
        evaluator = ExplorerAgent(MDP, input_policy = Learner.create_learned_softmax_policy(temp))
        evaluator.explore(episode_limit = 50)
        r = [record[-1][3] for record in evaluator.episodic_record]
        l = [len(record) for record in evaluator.episodic_record]

        rewards.append(r)
        mean_rewards.append(np.mean(r))
        std_rewards.append(np.std(r))
        mean_episode_length.append(np.mean(l))

        #print(mean_rewards[-1])


    return rewards, mean_rewards, std_rewards, mean_episode_length, ep


if __name__ == '__main__':
    a=1
    MDP= CreateDinnerMDP()
    #MDP.specification_fsm.visualize(prog = 'twopi')
#    MDP, fsm, control_mdp = CreateSpecMDP3(reward_type = 'chance_constrained', risk_level=0.61)
#    fsm.visualize()

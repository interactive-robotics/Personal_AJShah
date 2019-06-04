#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 15:37:31 2019

@author: ajshah
"""

import pandas as pd
import seaborn as sns
import pickle
import matplotlib
import matplotlib.pyplot as plt
import os
import pickle
from mod_relational import *


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

def TrainAndTest(LearnerType, MDP, directory, nRuns = 10, episodes = 1000, steps = 1, temp=0.01, verbose=True):
    
    if not os.path.exists(directory):
        os.mkdir(directory)
    for i in range(nRuns):
        print(f'Run: {i} of {nRuns}')
        agent = LearnerType(MDP)
        LCRecord = RecordLearningCurve(MDP, agent, max_episodes=episodes, 
                                       steps = steps, temp = temp, verbose=verbose)
        with open(os.path.join(directory, f'LC{i}'),'wb') as file:
            pickle.dump({'LC':LCRecord},file)
        del agent

        
def ReadLCData(directory, label):
    RawData = {}
    for r,d,files in os.walk(directory):
        for (i,f) in enumerate(files):
            Data = pickle.load(open(os.path.join(r,f),'rb'))
            reward, mean_reward, reward_std, _, episodes = Data['LC']
            
            for replicates, ep in zip(reward, episodes):
                for x in replicates:
                    RawData[len(RawData)] = [x,ep,label,i]
    return pd.DataFrame.from_dict(RawData, orient = 'index', 
                                  columns = ['Mean Terminal Reward', 'Episode', 'Learning agent','run'])


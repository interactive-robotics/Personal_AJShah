#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 11:17:52 2019

@author: ajshah
"""

from SpecificationMDP import *
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

class ExplorerAgent():
    
    def __init__(self, MDP:SpecificationMDP, input_policy = None):
        
        self.MDP = MDP
        self.exploration_graph = nx.DiGraph()
        self.episodic_record = []
        self.policy = self.default_policy if input_policy is None else input_policy
        self.visited = set()
    
    
    def default_policy(self, state = None):
        '''Usually overridden by the policy of the learning program'''
        #For the base class the default policy is just random exploration
        if state == None: state = self.MDP.state()
        action_list = self.MDP.get_actions(state)
        action = np.random.choice(action_list)
        return action
    
    def learn(self, old_state, action, new_state, reward):
        return None
    
    def explore(self, episode_limit = 100, action_limit = 10000, verbose = False):
        #initialize the the specification MDP
        self.MDP.initialize_state()
        
        #Initialize exploration parameters
        stop = False
        self.add_to_visited(self.MDP.state)
        episode = 0
        action_count = 0
        episode_trajectory = []
        
        while not stop:
            
            if verbose and episode%100 == 0:
                print(f'\rTraining episode {episode}         ' , end='')
            
            #select the polci according to the exploration policy
            old_state = self.MDP.state
            action = self.policy(self.MDP.state)
            new_state, reward = self.MDP.transition(old_state, action)
            
            #increment action count and update the exploration record
            action_count = action_count + 1
            episode_trajectory.append((old_state, action, new_state, reward))
            
            #update the exploration graph
            self.add_to_visited(new_state)
            self.exploration_graph.add_edge(old_state, new_state, action=action)
            
            #learn the policy updates
            self.learn(old_state, action, new_state, reward)
            
            #check stop condition for action count
            stop = action_count >= action_limit
            
            #Now check for terminal conditions to reset episode:
            if self.MDP.is_terminal():
                #record the episode initialize the episodic trajectory
                self.episodic_record.append(episode_trajectory)
                episode_trajectory = []
                episode = episode + 1
                
                #reset the MDP
                self.MDP.initialize_state()
                
                #check for stop condition
                stop = stop or episode >= episode_limit
        self.episodic_record.append(episode_trajectory)
        return action_count, episode
    
    def add_to_visited(self, state):
        if state not in self.visited:
            self.visited = self.visited | {state}
            self.exploration_graph.add_node(state, name=len(self.exploration_graph.nodes))
    
    @property
    def node2id(self):
        return dict(self.exploration_graph.nodes(data='name'))
    
    @property
    def id2node(self):
        return dict([(v,k) for (k,v) in self.node2id.items()])
    
    @property
    def edges2actions(self):
        return dict(dict([((u,v),c) for (u,v,c) in self.exploration_graph.edges.data('action')]))
    
    @property
    def G(self):
        return self.exploration_graph #shorthand for exploration graph
    
    def visualize_exploration(self, coloring = 'reward', prog='dot'):
        
        pos = nx.drawing.nx_agraph.graphviz_layout(self.G, prog=prog)
        if coloring == 'reward':
            colors = [self.MDP.reward_function(node) for node in self.exploration_graph.nodes()]
        else:
            colors=None
        #start drawing
        
        if colors is not None:
            nx.draw_networkx(self.G, pos, with_labels = False, 
                             node_color = colors, cmap = 'coolwarm_r', vmin=-1.2, vmax = 1.2)
            nx.draw_networkx_labels(self.G, pos, self.node2id)
            nx.draw_networkx_edge_labels(self.G, pos, self.edges2actions)
        return colors
    
    @property
    def easy_episodic_record(self):
        
        easy_record = []
        
        for record in self.episodic_record:
            new_record = []
            for e in record:
                new_record.append((self.node2id[e[0]], e[1], self.node2id[e[2]], e[3]))
            easy_record.append(new_record)
        return easy_record
    
    @property
    def terminal_rewards(self):
        rewards = [entry[-1][3] for entry in self.episodic_record]
        return rewards

class QLearningAgent(ExplorerAgent):
    
    def __init__(self, MDP:SpecificationMDP, gamma = 0.99, learning_rate_schedule = None, input_policy = None, 
                 default_alpha = 0.3):
        #Call the base class constructor
        
        self.Q = {}
        self.gamma = gamma
        self.eps = 0.3
        self.learning_rate_schedule = self.default_learning_rate_schedule if learning_rate_schedule is None else learning_rate_schedule
        self.default_alpha = default_alpha
        super().__init__(MDP, input_policy=input_policy)
    
    def add_to_visited(self, state):
        #reverify that state is not in visited list
        if state not in self.visited:
            self.visited = self.visited | {state}
            self.visited = self.visited | {state}
            self.exploration_graph.add_node(state, name=len(self.exploration_graph.nodes))
            actions = self.MDP.get_actions(state)
            for a in actions:
                self.Q[(state, a)] = -0.5

    def get_max_Q_action(self, state):
        actions = self.MDP.get_actions(state)
        QValues = np.array([self.Q[(state, a)] for a in actions])
        max_Q = np.max(QValues)
        selected_action = actions[np.argmax(QValues)]
        return max_Q, selected_action, QValues
    
    def default_policy(self, state):
        #check if the state has been visited
        if state not in self.visited:
            self.add_to_visited(state)
        
        #Decide whether to explore or exploit
        if np.random.rand() < self.eps: #explore
            actions = self.MDP.get_actions(state)
            action = np.random.choice(actions)
        else: #exploit
            maxQ, action,_ = self.get_max_Q_action(state)
        
        return action
    
    def learn(self, old_state, action, new_state, reward):
        oldQ = self.Q[(old_state, action)]
        
        Q_to_go, _, _ = self.get_max_Q_action(new_state)
        targetQ = reward + self.gamma*(Q_to_go)
        
        updatedQ = (1-self.alpha)*oldQ + self.alpha*targetQ
        self.Q[(old_state, action)] = updatedQ
    
    #def learn_on_buffer
        
    def default_learning_rate_schedule(self, episodes): 
        return self.default_alpha  #A constant learning rate schedule
    
    @property
    def episodes(self):
        return len(self.episodic_record)
    
    @property
    def alpha(self):
        return self.learning_rate_schedule(self.episodes)
    
    @property
    def learned_policy(self):
        
        def policy(state):
            maxQ, action, _ = self.get_max_Q_action(state)
            return action
        return policy
        

if __name__ == '__main__':
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

    '''Testing random exploration agent'''
    '''
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type='chance_constrained', risk_level=0.3)
    control_mdp = SyntheticMDP(5,4)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    
    explorer = ExplorerAgent(MDP)
    explorer.explore(episode_limit = 5000, verbose=True)
    explorer.visualize_exploration(prog='twopi')
    '''
    
    explorer = ExplorerAgent(MDP)
    random_exploration_policy = explorer.policy
    
    print('Initializing q-learning with random exploration')
    q_learning_agent = QLearningAgent(MDP)
    #initialize with a random policy
    q_learning_agent.policy = random_exploration_policy
    q_learning_agent.explore(episode_limit = 10000, verbose=True, action_limit = 20000)
    
    learned_policy = q_learning_agent.learned_policy
    explorer = ExplorerAgent(MDP, input_policy = learned_policy)
    explorer.explore(episode_limit = 10)
    plt.figure()
    explorer.visualize_exploration()
    
    print('refining learned policy')
    q_learning_agent.policy = q_learning_agent.default_policy
    q_learning_agent.explore(episode_limit = 100)
    learned_policy = q_learning_agent.learned_policy
    
    print('Testing learned policy')
    explorer = ExplorerAgent(MDP, input_policy = learned_policy)
    explorer.explore(episode_limit = 10)
    plt.figure()
    explorer.visualize_exploration()





















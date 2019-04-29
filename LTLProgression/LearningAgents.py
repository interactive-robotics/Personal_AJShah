#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 15:38:15 2019

@author: ajshah
"""

from Exploration import *
class QLearningAgent(ExplorerAgent):
    
    def __init__(self, MDP:SpecificationMDP, gamma = 0.99, learning_rate_schedule = None, input_policy = None, 
                 default_alpha = 0.3, counterfactual_updates = False, soft_bellman=False):
        #Call the base class constructor
        
        self.Q = {}
        self.gamma = gamma
        self.eps = 0.2
        self.learning_rate_schedule = self.default_learning_rate_schedule if learning_rate_schedule is None else learning_rate_schedule
        self.default_alpha = default_alpha
        super().__init__(MDP, input_policy=input_policy)
    
    def add_to_visited(self, state):
        #reverify that state is not in visited list
        if state not in self.visited:
            self.visited = self.visited | {state}
            self.exploration_graph.add_node(state, name=str(len(self.exploration_graph.nodes)))
            actions = self.MDP.get_actions(state)
            for a in actions:
                self.Q[(state, a)] = self.Q_init
        

    def get_max_Q_action(self, state):
        actions = self.MDP.get_actions(state)
        
        if state not in self.visited:
            for a in actions:
                self.Q[(state, a)] = self.Q_init
        
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
    
    @property
    def learned_softmax_policy(self):
        
        def policy(state):
            _,_, Q_values = self.get_max_Q_action(state)
            actions = self.MDP.get_actions(state)
            #probs = softmax(Q_values)
            action = np.random.choice(actions, p = softmax(Q_values))
            return action
    
    def visualize_exploration(self, coloring = 'reward', prog='dot'):
        
        pos = nx.drawing.nx_agraph.graphviz_layout(self.G, prog=prog)
        if coloring == 'reward':
            colors = [self.MDP.reward_function(node, force_terminal=True) for node in self.exploration_graph.nodes()]
        elif coloring == 'Q':
            colors = [self.get_max_Q_action(node)[0] for node in self.exploration_graph.nodes()]
        else:
            colors=None
        #start drawing
        
        if colors is not None:
            nx.draw_networkx(self.G, pos, with_labels = False, 
                             node_color = colors, cmap = 'coolwarm_r', vmin=np.min(colors), vmax = np.max(colors))
        else:
            nx.draw_networkx(self.G, pos, with_labels = False)
        nx.draw_networkx_labels(self.G, pos, self.node2id)
        nx.draw_networkx_edge_labels(self.G, pos, self.edges2actions)
        return colors

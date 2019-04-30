#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 15:38:15 2019

@author: ajshah
"""

from Exploration import *
from scipy.special import softmax
from scipy.special import logsumexp
from utils import *
from joblib import Parallel, delayed


class QLearningAgent(ExplorerAgent):
    
    #All the exploration policies for the QLearningAgent must be defined in class
    
    def __init__(self, MDP:SpecificationMDP, gamma = 0.98, learning_rate_schedule = None,
                 default_alpha = 0.3, counterfactual_updates = False, soft_bellman=False):
        #Call the base class constructor
        
        super().__init__(MDP)
        #At this point it should be initiated with a random exploration policy and will be overridden in this function
        self.Q = {}
        self.gamma = gamma
        self.eps = 0.2
        self.learning_rate_schedule = self.default_learning_rate_schedule if learning_rate_schedule is None else learning_rate_schedule
        self.default_alpha = default_alpha
        self.soft_bellman = soft_bellman
        self.counterfactual_updates = counterfactual_updates
        
        self.policy = self.softmax_exploration_policy if soft_bellman else self.maxQ_exploration_policy
        self.learn = self.counterfactual_learn if self.counterfactual_updates else self.standard_learn
        
        
    
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
   
    
    def standard_learn(self, old_state, action, new_state, reward):
        oldQ = self.Q[(old_state, action)]
        
        if self.soft_bellman:
            Q_to_go, _, _ = self.get_softmax_Q_action(new_state)
        else:
            Q_to_go, _, _ = self.get_max_Q_action(new_state)
        
        targetQ = reward + self.gamma*(Q_to_go)
        updatedQ = (1-self.alpha)*oldQ + self.alpha*targetQ
        self.Q[(old_state, action)] = updatedQ
        
        
    def counterfactual_learn(self, old_state, action, new_state, reward):
        
        #Get the new control state
        new_spec_state, new_control_state = self.MDP.decompose_state(new_state)
        old_spec_state, old_control_state = self.MDP.decompose_state(old_state)
        #trace_slice = self.MDP.control_mdp.create_observations(new_control_state)
        
        #Collect all specification states
        cf_record = []
        
        transitions = Parallel(n_jobs=8,require='sharedmem')(delayed(self.create_cf_record)(old_control_state, new_control_state, cf_spec_state) for cf_spec_state in self.MDP.specification_fsm.states2id.keys())
        
        for transition in transitions:
            self.add_to_visited(transition[0])
            self.add_to_visited(transition[1])
            self.exploration_graph.add_edge(transition[0], transition[1], action=action)
            cf_record.append((transition[0], action, transition[1], transition[2]))
        
#        for cf_spec_state in self.MDP.specification_fsm.states2id.keys():
#            if not IsTerminalState(cf_spec_state):
#                old_cf_state = self.MDP.create_state(cf_spec_state, old_control_state)
#                self.add_to_visited(old_cf_state)
#                new_cf_spec_state, cf_reward = self.MDP.transition_specification_state(old_cf_state, new_control_state)
#                new_cf_state = self.MDP.create_state(new_cf_spec_state, new_control_state)
#                self.add_to_visited(new_cf_state)
#                self.exploration_graph.add_edge(old_cf_state, new_cf_state, action = action)
#                cf_record.append((old_cf_state, action, new_cf_state, cf_reward))
            
            
        # For each counterfactual state.Q values need to be retrieved. This will be slow but can be vectorized for speed up
        #Q_updater = lambda record: self.Q_update(*record)
        QUpdated = Parallel(n_jobs = 8, require='sharedmem')(delayed(self.Q_updater)(record) for record in cf_record)
        
        for (i, record) in enumerate(cf_record):
            self.Q[(record[0],record[1])] = QUpdated[i]
        
    def create_cf_record(self, old_control_state, new_control_state, cf_spec_state):
        old_cf_state = self.MDP.create_state(cf_spec_state, old_control_state)
        new_cf_spec_state, cf_reward = self.MDP.transition_specification_state(old_cf_state, new_control_state)
        new_cf_state = self.MDP.create_state(new_cf_spec_state, new_control_state)
        return old_cf_state, new_cf_state, cf_reward
        
    def Q_updater(self, record):
        (old_state, action, new_state, reward) = record
        oldQ = self.Q[(old_state, action)]
        
        if self.soft_bellman:
            Q_to_go, _, _ = self.get_softmax_Q_action(new_state)
        else:
            Q_to_go,_ ,_ = self.get_max_Q_action(new_state)
        
        targetQ = reward + self.gamma*Q_to_go
        
        updatedQ = (1-self.alpha)*oldQ + self.alpha*targetQ
        return updatedQ
        
    @property
    def learned_policy(self):
        
        def policy(state):
            maxQ, action, _ = self.get_max_Q_action(state)
            return action
        return policy
    
    @property
    def learned_softmax_policy(self):
        
        def policy(state):
            softmax_Q,action, _ = self.get_softmax_Q_action(state)
            return action
        return policy
    
    def create_learned_softmax_policy(self, temperature = 1):
        
        def policy(state):
            softmax_Q, action, _ = self.get_softmax_Q_action(state, temperature)
            return action
        return policy
    
    
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
    
    
    def get_softmax_Q_action(self, state, temperature = 1):
        actions = self.MDP.get_actions(state)
        
        if state not in self.visited:
            for a in actions:
                self.Q[(state, a)] = self.Q_init
        
        QValues = np.array([self.Q[(state, a)] for a in actions])/temperature
        softmax_Q = temperature*logsumexp(QValues)
        selected_action = np.random.choice(actions, p = softmax(QValues))
        return softmax_Q, selected_action, QValues
    
    
    def maxQ_exploration_policy(self, state):
        #check if the state has been visited
        if state not in self.visited:
            self.add_to_visited(state)
        
        actions = self.MDP.get_actions(state)
        
        if np.random.rand() < self.eps:
            action = np.random.choice(actions)
        else:
            _, action, _ = self.get_max_Q_action(state)
        return action
    
    def softmax_exploration_policy(self, state):
        if state not in self.visited: self.add_to_visited(state)
        actions = self.MDP.get_actions(state)
        _, action, _ = self.get_softmax_Q_action(state)
        return action

        
    def default_learning_rate_schedule(self, episodes): 
        return self.default_alpha  #A constant learning rate schedule
    
    @property
    def episodes(self):
        return len(self.episodic_record)
    
    @property
    def alpha(self):
        return self.learning_rate_schedule(self.episodes)
    

    
if __name__ == '__main__':
    #This should behave just like the vanilla RL agent we had defined in Exploration.py
    
    MDP = CreateSampleMDP()
    
    '''testing regular q learning'''
#    print('Testing vanilla q-learning agent')
#    q_learning_agent = QLearningAgent(MDP)
#    #initialize with a random policy
#    
#    print('refining learned policy')
#    #q_learning_agent.policy = q_learning_agent.default_policy
#    q_learning_agent.explore(episode_limit = 10000, action_limit=50000, verbose=True)
#    learned_policy = q_learning_agent.learned_policy
#    
#    print('Testing learned policy')
#    explorer = ExplorerAgent(MDP, input_policy = learned_policy)
#    explorer.explore(episode_limit = 100)
#    plt.figure()
#    explorer.visualize_exploration(prog='twopi')
#    
#    plt.figure()
#    explorer2 = ExplorerAgent(MDP, input_policy=q_learning_agent.learned_softmax_policy)
#    explorer2.explore(episode_limit=100)
#    explorer2.visualize_exploration(prog='twopi')
    
    '''testing softmax agent'''
#    print('Testing softmax agent')
#    softmax_agent = QLearningAgent(MDP, soft_bellman=True)
#    softmax_agent.Q_init = 0
#    softmax_agent.explore(episode_limit = 100, action_limit =  100000, verbose=True)
#    
#    print('Testing learned max policy')
#    explorer3 = ExplorerAgent(MDP, input_policy=softmax_agent.learned_policy)
#    explorer3.explore(episode_limit=100)
#    
#    plt.figure()
#    explorer3.visualize_exploration(prog = 'twopi')
#    
#    print('Testing learned softmax policy')
#    explorer4 = ExplorerAgent(MDP, input_policy = softmax_agent.learned_softmax_policy)
#    explorer4.explore(episode_limit=100)
#    plt.figure()
#    explorer4.visualize_exploration(prog = 'twopi')
#    
    '''testing counterfactual q value updates'''
    cf_q_agent = QLearningAgent(MDP, counterfactual_updates=True, default_alpha = 0.5)
    cf_q_agent.explore(episode_limit = 100, action_limit=20000,  verbose = True)
    #cf_q_agent.visualize_exploration(prog='twopi')


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 19:06:15 2019

@author: ajshah
"""

from SpecificationFSMTools import *
from ControlMDP import *
import matplotlib.pyplot as plt

class SpecificationMDP():
    
    def __init__(self, specification_fsm: SpecificationFSM, control_mdp: ControlMDP):
        
        if not isinstance(specification_fsm, SpecificationFSM): raise TypeError(
                'specification_fsm should be an instance of SpecificationFSM')
        
        if not isinstance(control_mdp, ControlMDP): raise TypeError(
                'control_mdp should be an instance of ControlMDP')
        
        self.specification_fsm = specification_fsm
        self.control_mdp = control_mdp
        
        self.state = self.initialize_state(specification_fsm.id2states[0]) # we will use the string version to represent the specification_mdp state
    
    def initialize_state(self, specification_state=None):
        if specification_state==None: specification_state = self.specification_fsm.id2states[0]
        state = self.create_state(specification_state, self.control_mdp.reset_initial_state())
        self.state = state
        return state
    
    def decompose_state(self, state):
        return state[0], state[1]
    
    def create_state(self, specification_state, control_state):
        return (specification_state, control_state)
    
    def is_terminal(self, state=None):
        if state==None: state = self.state
        specification_state, control_state = self.decompose_state(state)
        
        if type(specification_state)==int:
            specification_state = self.specification_fsm.id2states[specification_state]
        
        return ((specification_state in self.specification_fsm.terminal_states) 
                or 
                self.control_mdp.is_terminal(control_state))
    
    def get_actions(self, state=None):
        if state == None: state = self.state
        
        specifcation_state, control_state = self.decompose_state(state)
        return self.control_mdp.get_actions(control_state)
    
    def reward_function(self, state=None):
        if state==None: state = self.state
        specification_state, _ = self.decompose_state(state)
        return self.specification_fsm.reward_function(specification_state)
    
    def transition(self, state, action):
        
        if not action in self.get_actions(state): raise Exception('Invalid action for this state')
        
        specification_state, control_state = self.decompose_state(state)
        #Use the action to progress the control state
        new_control_state = self.control_mdp.transition(action)
        trace_slice = self.control_mdp.create_observations(new_control_state)
        new_specification_state = self.specification_fsm.transition_function(specification_state, trace_slice)
        
        new_state = self.create_state(new_specification_state, new_control_state)
        reward = self.reward_function(new_state)
        
        #update the MDP state
        self.state = new_state
        return new_state, reward
    
    def transition_specification_state(self, old_state, new_control_state):
        #Only update the specification state as per the new control state. Used for off-policy updates
        #returns the new specification state and the reward
        old_specification_state, _ = self.decompose_state(old_state)
        trace_slice = self.control_mdp.create_observations(new_control_state)
        new_specification_state = self.specification_fsm.transition_function(old_specification_state, trace_slice)
        
        reward = self.specification_fsm.reward_function(new_specification_state)
        return new_specification_state, reward
    
    @property
    def easy_state(self):
        #converts the specification_state to an index
        specification_state, control_state = self.decompose_state(self.state)
        specification_id = self.specification_fsm.states2id[specification_state]
        return (specification_id, control_state)
    
    @easy_state.setter
    def easy_state(self, idx):
        specification_state = self.specification_fsm.id2states[idx]
        _, control_state = self.decompose_state(self.state)
        self.state = self.create_state(specification_state, control_state)
        

def RandomExploration(specification_mdp:SpecificationMDP, episode_limit=100, action_limit=20000, verbose=False):
    
    #initialize the MDP state
    specification_mdp.initialize_state()
    exploration_graph = nx.DiGraph()
    episodic_record = []
    stop = False
    visited = set([specification_mdp.state])
    
    episode = 0
    action_count = 0
    episode_trajectory = []
    
    while not stop:
        if verbose and episode%100 == 0 :
            print(f'\rTraining episode {episode}         ' , end='')
        #Get actions to perform and sample a random action
        #print(episode)
        #check if we are in a terminal state

        
        available_actions = specification_mdp.get_actions()
        action = np.random.choice(available_actions)
        old_state = specification_mdp.state
        new_state, reward = specification_mdp.transition(specification_mdp.state, action)
        episode_trajectory.append((old_state, action, new_state, reward))
        action_count = action_count + 1
        
        #Add unvisited node to graph
        if new_state not in visited:
            visited = visited|{new_state}
            exploration_graph.add_node(new_state, name = len(exploration_graph.nodes))
        
        exploration_graph.add_edge(old_state, new_state, action = action)
        
        stop = action_count >= action_limit
        
        if specification_mdp.is_terminal():
            #record episode trajectory so far and initiate new trajectory
            episodic_record.append(episode_trajectory)
            episode_trajectory = []
            
            episode = episode+1 #episodes completed
            
            specification_mdp.initialize_state()
            stop = stop or episode >= episode_limit
    
    return exploration_graph, episodic_record, episode, action_count


if __name__ == '__main__':
    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    TraceSlice = GetTraceSlice(SampleSignal,0)
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas_synth = np.array(Formulas)[idx]
    Probs = np.array(Prob)[idx]
    ProgressedFormulas = np.array([ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas_synth])
    
    specification_fsm = SpecificationFSM(ProgressedFormulas, Probs, reward_type='chance_constrained', risk_level=0.3)
    control_mdp = SyntheticMDP(5, 4)
    MDP = SpecificationMDP(specification_fsm, control_mdp)
    
    G, episodic_record, episodes, action_count = RandomExploration(MDP, episode_limit=5000)
    
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    node_dict = dict(G.nodes(data='name'))
    edge_dict = dict([((u,v),c) for (u,v,c) in G.edges.data('action')])
    
    nx.draw_networkx(G, pos, with_labels=False)
    nx.draw_networkx_labels(G, pos, node_dict)
    nx.draw_networkx_edge_labels(G, pos, edge_dict)
    
    easy_episodic_record = []
    
    for record in episodic_record:
        new_record = []
        for entry in record:
            new_record.append((node_dict[entry[0]], entry[1], node_dict[entry[2]], entry[3]))
        easy_episodic_record.append(new_record)
        
    terminal_id = [records[-1][2] for records in easy_episodic_record]
    id2nodes = dict([(v,k) for (k,v) in node_dict.items()])
    final_rewards = [record[-1][3] for record in easy_episodic_record]
    
    terminal_states = [id2nodes[idx] for idx in terminal_id]
    
    #replotiing with final rewards
    colors = [MDP.reward_function(node) for node in G.nodes()]
    
    plt.figure()
    nx.draw_networkx(G, pos, with_labels=False, node_color=colors, cmap='coolwarm_r', vmin=-1.2, vmax=1.2)
    nx.draw_networkx_labels(G, pos, node_dict)
    nx.draw_networkx_edge_labels(G, pos, edge_dict)
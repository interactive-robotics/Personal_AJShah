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
        




if __name__ == '__main__':
    a=1
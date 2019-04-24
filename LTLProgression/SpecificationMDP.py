#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 19:06:15 2019

@author: ajshah
"""

from SpecificationFSMTools import *
from ControlMDP import *

class SpecificationMDP():
    
    def __init__(specification_fsm: SpecificationFSM, control_mdp: ControlMDP):
        
        if not isinstance(specification_fsm, SpecificationMDP): raise TypeError(
                'specification_fsm should be an instance of SpecificaionFSM')
        
        if not isinstance(control_mdp, ControlMDP): raise TypeError(
                'control_mdp should be an instance of ControlMDP')
        
        self.specificaion_fsm = specification_fsm
        self.control_mdp = control_mdp
        
        self.state = self.initialize_state(0)
    
    def initialize_state(self, specification_state):
        state = self.create_state(specificaion_state, control_mdp.reset_initial_state())
        self.state = state
        return state
    
    def decompose_state(self, state):
        return state[0], state[1]
    
    def create_state(self, specificaion_state, control_state):
        return (specification_state, control_state)


if __name__ == '__main__':
    
    
    
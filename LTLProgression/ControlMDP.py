#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 17:33:44 2019

@author: ajshah
"""

from numpy.random import binomial

class ControlMDP():
    
    def __init__(self):
        self.state = None
    
    def reset_initial_state(self):
        return self.state
    
    def transition(self, action):
        raise NotImplementedError
    
    def get_actions(self, state):
        raise NotImplementedError
    
    def create_observations(self, state=None):
        raise NotImplementedError



class SyntheticMDP(ControlMDP):
    
    def __init__(self, n_threats, n_waypoints, accessibility=None):
        ControlMDP.__init__(self)
        self._n_threats = n_threats
        self._n_waypoints = n_waypoints
        self.failure_prob = 0.2
        self.state = self.reset_initial_state()
        if accessibility == None: accessibility = [True]*n_waypoints
        self.accessibility = accessibility
        
    
    def reset_initial_state(self, stateful=True):
        threat_tuple = tuple([False]*self._n_threats)
        waypoint_tuple = tuple([False]*self._n_waypoints)
        state = self.create_state(threat_tuple, waypoint_tuple)
        if stateful:
            self.state = state
        return state
    
    def decompose_state(self, state):
        threat_values = list(state[0:self._n_threats])
        waypoint_values = list(state[self._n_threats::])
        return threat_values, waypoint_values
    
    def create_state(self, threat_tuple, waypoint_tuple):
        return (*threat_tuple, *waypoint_tuple)
    
    def get_actions(self, state):
        threat_actions = [f'T{i}' for i in range(self._n_threats)]
        waypoint_actions = [f'W{i}' for i in range(self._n_waypoints)]
        return [*threat_actions, *waypoint_actions]
    
    def transition(self, action):
        
        if action not in self.get_actions(self.state): raise Exception('Invalid action')
        
        threat_tuple, waypoint_tuple = self.decompose_state(self.state)
        
        #Determine action type
        if action[0] == 'T':
            threat_index = int(action[1::])
            #Get to threat_index
            if binomial(1,self.failure_prob):
                #Failure to execute condition and return the old state
                new_state = self.state
            else:
                #reset all values to False and set threat i to true
                threats, waypoints = self.decompose_state(self.reset_initial_state(stateful=False))
                threats[threat_index] = True
                new_state = MDP.create_state(threats, waypoints)
        else:
            waypoint_index = int(action[1::])
            if binomial(1, self.failure_prob):
                #failed action
                new_state = self.state
            else:
                threats, waypoints = self.decompose_state(self.reset_initial_state(stateful=False))
                if self.accessibility[waypoint_index]:
                    waypoints[waypoint_index] = True
                new_state = MDP.create_state(threats, waypoints)
        
        self.state = new_state
        return new_state
    
    def create_observations(self, state=None):
        
        if state==None: state = self.state
        
        TraceSlice = {}
        #Add all the threat observations
        threats, waypoints = self.decompose_state(state)
        for i in range(len(threats)):
            TraceSlice[f'T{i}'] = threats[i]
        for i in range(len(waypoints)):
            TraceSlice[f'W{i}'] = waypoints[i]
        return TraceSlice

if __name__ == '__main__':
    MDP = SyntheticMDP(5,4, accessibility=[False, True, True, True])
    

# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Wed Apr 24 17:33:44 2019

@author: ajshah
"""

from numpy.random import binomial
import numpy as np

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

    def is_terminal(self, state=None):
        return False



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
                new_state = self.create_state(threats, waypoints)
        else:
            waypoint_index = int(action[1::])
            if binomial(1, self.failure_prob):
                #failed action
                new_state = self.state
            else:
                threats, waypoints = self.decompose_state(self.reset_initial_state(stateful=False))
                if self.accessibility[waypoint_index]:
                    waypoints[waypoint_index] = True
                new_state = self.create_state(threats, waypoints)

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


class TableMDP(ControlMDP):
    def __init__(self, failure_prob=0.2, num_steps=1):
        ControlMDP.__init__(self)

        # State space:
        # num_dofs = num_objs
        # num_states = (num_steps+1) ^ num_objs
        # Each dimension of a state represents an object.
        # The state value along a dimension is an int,
        # representing the current progress of that object.
        # state[0] = 0 => object 0 is available for pickup and place.
        # state[0] = 1 => robot has just finished step 1 for object 0.
        # ...
        # state[0] = num_steps => robot has just finished object 0.

        self.objId_2_objName = {
            0: "DinnerPlate",
            1: "SmallPlate",
            2: "Bowl",
            3: "Knife",
            4: "Fork",
            5: "Spoon",
            6: "Mug",
            7: "Glass"
        }
        self.num_objs = len(self.objId_2_objName)
        #assert (set(self.objId_2_objName.keys()) == set(range(self.num_objs)))
        self.num_steps = num_steps

        self.failure_prob = failure_prob

        self.state = self.reset_initial_state()
        print(self.to_string_state(self.state))

    def create_state(self, obj_progresses):
        return tuple(obj_progresses)

    def reset_initial_state(self, stateful=True):
        obj_progresses = tuple([0] * self.num_objs)
        state = self.create_state(obj_progresses=obj_progresses)
        if stateful:
            self.state = state
        return state

    def decompose_state(self, state):
        obj_progresses = tuple(state)
        return obj_progresses

    def to_string_state(self, state):
        obj_progresses = self.decompose_state(state)
        s = "@["
        for i, k in enumerate(self.objId_2_objName.keys()):
            v = self.objId_2_objName[k]
            s += v + "=" + str(obj_progresses[k]) + ", "
        s += "]"
        return s

    def transition(self, action):
        if action not in self.get_actions(self.state):
            raise Exception('Invalid action=' + str(action))
        obj_progresses = list(self.decompose_state(self.state))

        new_state = None
        if binomial(1, self.failure_prob):
            # 1. Failure to execute condition
            # and return the old state.
            new_state = self.state
        else:
            # TODO 2. If the object has been finished,
            # do another action on it won't change anything.
            obj_progresses[action] = min((obj_progresses[action] + 1),
                                         self.num_steps)
            new_state = self.create_state(obj_progresses=tuple(obj_progresses))
        self.state = new_state
        return new_state

    def get_actions(self, state):
        obj_progresses = self.decompose_state(state)

        # TODO: 1. If obj has been placed, specification should
        # prevent from the robot to place it again.
        # So here available actions include the objects that have
        # been finished.
        available_actions = range(self.num_objs)

        must_actions = []
        for i in range(self.num_objs):
            obj_progress = obj_progresses[i]
            # If the robot is in the middle of manipulating object i,
            # then we have to continue.
            if obj_progress != 0 and obj_progress != self.num_steps:
                must_actions.append(i)
        if len(must_actions) > 0:
            # TODO 2. Here some states might have more than 1
            # must_actions, but those states are not supposed to
            # be reachable in planning.
            return must_actions
        else:
            return available_actions

    def create_observations(self, state=None):
        if state == None:
            state = self.state
        TraceSlice = {}
        # 1. Threat - colliding with threat - ignored here
        TraceSlice['T0'] = False
        # 2. Waypoints - object is in place
        obj_progresses = self.decompose_state(state)
        for obj, prog in enumerate(obj_progresses):
            key = "W" + str(obj)
            if prog == self.num_steps:
                TraceSlice[key] = True
            else:
                TraceSlice[key] = False
        # 3. object needs to be placed
        for obj in range(self.num_objs):
            key = "P" + str(obj)
            TraceSlice[key] = True
        return TraceSlice

    def is_terminal(self, state=None):
        # Always False in this domain.
        # No serious failures defined.
        return False

    # For testing
    def enumerate_all_states(self):
        self.dimensions = [self.num_steps + 1 for i in range(self.num_objs)]

        # Note that we use int32 here. Change to int64 if necessary.
        self.num_states = np.prod(np.array(self.dimensions))
        assert (self.num_states < np.iinfo(np.int32).max)
        self.num_states = int(self.num_states.astype(np.int32))
        print("dimensions=", self.dimensions, "num_states=", self.num_states)
        self.ndarray_style = "C"

    def ind2sub(self, ind):
        """int -> tuple"""
        assert (ind < self.num_states and ind >= 0)
        return np.unravel_index(
            indices=ind, dims=tuple(self.dimensions), order=self.ndarray_style)

    def sub2ind(self, subscripts):
        """tuple -> int"""
        assert (len(subscripts) == len(self.dimensions))
        for i in range(len(subscripts)):
            assert (subscripts[i] < self.dimensions[i] and subscripts[i] >= 0)
        return np.ravel_multi_index(
            multi_index=subscripts,
            dims=tuple(self.dimensions),
            order=self.ndarray_style)

class SmallTableMDP(ControlMDP):
    def __init__(self, failure_prob=0.0, num_steps=1):
        ControlMDP.__init__(self)

        # State space:
        # num_dofs = num_objs
        # num_states = (num_steps+1) ^ num_objs
        # Each dimension of a state represents an object.
        # The state value along a dimension is an int,
        # representing the current progress of that object.
        # state[0] = 0 => object 0 is available for pickup and place.
        # state[0] = 1 => robot has just finished step 1 for object 0.
        # ...
        # state[0] = num_steps => robot has just finished object 0.

        self.objId_2_objName = {
            0: "DinnerPlate",
            1: "SmallPlate",
            2: "Bowl",
            3: "Knife",
            4: "Fork",
        }
        self.num_objs = len(self.objId_2_objName)
        #assert (set(self.objId_2_objName.keys()) == set(range(self.num_objs)))
        self.num_steps = num_steps

        self.failure_prob = failure_prob

        self.state = self.reset_initial_state()
        print(self.to_string_state(self.state))

    def create_state(self, obj_progresses):
        return tuple(obj_progresses)

    def reset_initial_state(self, stateful=True):
        obj_progresses = tuple([0] * self.num_objs)
        state = self.create_state(obj_progresses=obj_progresses)
        if stateful:
            self.state = state
        return state

    def decompose_state(self, state):
        obj_progresses = tuple(state)
        return obj_progresses

    def to_string_state(self, state):
        obj_progresses = self.decompose_state(state)
        s = "@["
        for i, k in enumerate(self.objId_2_objName.keys()):
            v = self.objId_2_objName[k]
            s += v + "=" + str(obj_progresses[k]) + ", "
        s += "]"
        return s

    def transition(self, action):
        if action not in self.get_actions(self.state):
            raise Exception('Invalid action=' + str(action))
        obj_progresses = list(self.decompose_state(self.state))

        new_state = None
        if binomial(1, self.failure_prob):
            # 1. Failure to execute condition
            # and return the old state.
            new_state = self.state
        else:
            # TODO 2. If the object has been finished,
            # do another action on it won't change anything.
            obj_progresses[action] = min((obj_progresses[action] + 1),
                                         self.num_steps)
            new_state = self.create_state(obj_progresses=tuple(obj_progresses))
        self.state = new_state
        return new_state

    def get_actions(self, state):
        obj_progresses = self.decompose_state(state)

        # TODO: 1. If obj has been placed, specification should
        # prevent from the robot to place it again.
        # So here available actions include the objects that have
        # been finished.
        available_actions = range(self.num_objs)

        must_actions = []
        for i in range(self.num_objs):
            obj_progress = obj_progresses[i]
            # If the robot is in the middle of manipulating object i,
            # then we have to continue.
            if obj_progress != 0 and obj_progress != self.num_steps:
                must_actions.append(i)
        if len(must_actions) > 0:
            # TODO 2. Here some states might have more than 1
            # must_actions, but those states are not supposed to
            # be reachable in planning.
            return must_actions
        else:
            return available_actions

    def create_observations(self, state=None):
        if state == None:
            state = self.state
        TraceSlice = {}
        # 1. Threat - colliding with threat - ignored here
        #TraceSlice['T0'] = False
        # 2. Waypoints - object is in place
        obj_progresses = self.decompose_state(state)
        for obj, prog in enumerate(obj_progresses):
            key = "W" + str(obj)
            if prog == self.num_steps:
                TraceSlice[key] = True
            else:
                TraceSlice[key] = False
        # 3. object needs to be placed
        for obj in range(self.num_objs):
            key = "P" + str(obj)
            TraceSlice[key] = True
        return TraceSlice

    def is_terminal(self, state=None):
        # Always False in this domain.
        # No serious failures defined.
        return False

    # For testing
    def enumerate_all_states(self):
        self.dimensions = [self.num_steps + 1 for i in range(self.num_objs)]

        # Note that we use int32 here. Change to int64 if necessary.
        self.num_states = np.prod(np.array(self.dimensions))
        assert (self.num_states < np.iinfo(np.int32).max)
        self.num_states = int(self.num_states.astype(np.int32))
        print("dimensions=", self.dimensions, "num_states=", self.num_states)
        self.ndarray_style = "C"

    def ind2sub(self, ind):
        """int -> tuple"""
        assert (ind < self.num_states and ind >= 0)
        return np.unravel_index(
            indices=ind, dims=tuple(self.dimensions), order=self.ndarray_style)

    def sub2ind(self, subscripts):
        """tuple -> int"""
        assert (len(subscripts) == len(self.dimensions))
        for i in range(len(subscripts)):
            assert (subscripts[i] < self.dimensions[i] and subscripts[i] >= 0)
        return np.ravel_multi_index(
            multi_index=subscripts,
            dims=tuple(self.dimensions),
            order=self.ndarray_style)


if __name__ == '__main__':
    MDP = SyntheticMDP(5,4, accessibility=[False, True, True, True])

    x = TableMDP(failure_prob=0.2, num_steps=2)

    # For testing
    x.enumerate_all_states()
    print("state, subscripts => actions")
    for s in range(x.num_states):
        sub = x.ind2sub(s)
        actions = x.get_actions(sub)
        print((s, sub, "=>", actions))

    print("subscripts => action => subscripts_prime")
    for s in range(x.num_states):
        sub = x.ind2sub(s)
        actions = x.get_actions(sub)
        for a in actions:
            x.state = sub
            sub_prime = x.transition(a)
            print((sub, "=>", a, "=>", sub_prime))

    print("state => observation")
    for s in range(x.num_states):
        sub = x.ind2sub(s)
        TraceSlice = x.create_observations(state=sub)
        d = {
            k: TraceSlice[k]
            for k in TraceSlice.keys() if "P" not in k and "T" not in k
        }
        print(sub, "=>", d)

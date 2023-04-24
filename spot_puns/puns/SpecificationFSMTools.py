#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: ajshah
"""

from puns.Progression import *
import numpy as np

class SpecificationFSM():

    def __init__(self, formulas=None, probs=None, reward_type = 'min_regret', risk_level = 0.05):
        # We do not need to assume whether these formulas are progressed formulas or single formulas.
        # We will assume that the formulas are unsorted

        sorted_formulas, sorted_probs, sel_formulas, sel_rewards = self.select_formulas(formulas, probs, reward_type,
                                                                                      risk_level)

        self._all_formulas = sorted_formulas
        self._all_probs = sorted_probs
        self._formulas = sel_formulas
        self._partial_rewards = sel_rewards

        states2id, edges = FindAllProgressions(self._formulas)
        id2states = dict([(v,k) for (k,v) in states2id.items()])

        self.states2id = states2id
        self.id2states = id2states
        self.edges = edges

        self.terminal_states = FindTerminalStates(states2id)
        self.reward_function = CreateReward(self._partial_rewards)
        self.graph = CreateGraph(states2id, edges)

    def transition_function(self, idx, TraceSlice):
        if type(idx) == int:
            state = self.id2states[idx]
        else:
            state = idx

        progressions = [ProgressSingleTimeStep(json.loads(formula), TraceSlice) for formula in state]
        next_state = tuple([json.dumps(prog_formula) for prog_formula in progressions])
        reward = self.reward_function(next_state)
        if type(idx) == int:
            return self.states2id[next_state]
        else:
            return next_state

    def select_formulas(self, formulas, probs, reward_type='min_regret', risk_level=0.05):

        idx = np.argsort(probs)[::-1]
        probs = np.array(probs)[idx]
        sorted_formulas = np.empty((len(idx),), dtype=object)
        for i in range(len(idx)):
            sorted_formulas[i] = formulas[idx[i]]
        formulas = sorted_formulas

        if reward_type not in set(['map','min_regret','max_cover','chance_constrained']):
            raise Exception('Unknown reward formulation')
        if reward_type == 'map':
            sel_formulas = np.empty((1,),dtype=object)
            sel_formulas[0] = formulas[0]
            sel_rewards = np.array([probs[0]])
        elif reward_type == 'chance_constrained':
            idx = 1
            while np.sum(probs[0:idx]) <= 1-risk_level:
                idx = idx+1
            sel_formulas = np.empty((idx,), dtype=object)
            for i in range(idx):
                sel_formulas[i] = formulas[i]
            sel_rewards = np.array(probs[0:idx])
        elif reward_type == 'max_cover':
            sel_formulas = formulas
            sel_rewards = np.ones(sel_formulas.shape)
        else:
            sel_formulas = formulas
            sel_rewards = probs
        return formulas, probs, sel_formulas, sel_rewards


    def visualize(self, colormap = 'reward', prog='twopi'):
        return VisualizeProgressionStates(self.states2id, self.edges, self.reward_function,
                                          colormap = colormap, terminal_states = self.terminal_states, prog = prog)



def CreateGraph(progression_states, edge_tuples):
    G = nx.DiGraph()
    for node in progression_states:
        G.add_node(progression_states[node])

    for e in edge_tuples:
        G.add_edge(progression_states[e[0]], progression_states[e[1]], transitions = e[2])
    return G


def FindAllProgressions(formulas):

    initial_state = tuple(json.dumps(formula) for formula in formulas)
    progression_states = {}
    progression_states[initial_state] = 0
    visited = [initial_state]
    queue = deque([initial_state])
    edges = {}

    while queue:

        state = queue.pop()
        Formulas = [json.loads(formula) for formula in state]
        #Determine the overall vocabulary
        vocabulary = reduce(
                            lambda vocab, form: GetVocabulary(form, vocab),
                            Formulas,
                            set())
        truth_assignments = get_all_truth_assignments(vocabulary)

        for truth_assignment in truth_assignments:

            progressed_formulas = [ProgressSingleTimeStep(formula, truth_assignment) for formula in Formulas]
            progressed_state = tuple(json.dumps(progressed_formula) for progressed_formula in progressed_formulas)
            edge = (state, progressed_state)

            if edge not in edges:
                edges[edge] = []

            edges[edge].append(truth_assignment)

            if progressed_state not in visited:
                visited.append(progressed_state)
                progression_states[progressed_state] = len(progression_states)
                queue.appendleft(progressed_state)

    edge_tuples = []
    for edge in edges:
        edge_tuples.append((edge[0], edge[1], edges[edge]))

    return progression_states, edge_tuples


def CreateReward(probs):
    #note that the probs must be marginal probabilities of all formulas. The state description might include fewer states
    #Thus np.sum(probs) = 1
    #and len(probs) == len(state)

    #This should return a function of the state that will generate the reward for entering that state. The max reward is 1
    #The minimum possible reward is -1

    def Reward(state, prev_state = None, force_terminal=False):

        if len(probs) >= len(state):
            #Select the probabilisties of the states being considered
            sel_probs = np.array(probs[0:len(state)])
            sel_probs = sel_probs/np.sum(sel_probs)
            #Check if the state is a reward giving state
            if IsTerminalState(state):
                #select the non-falsified formula
                if prev_state is None:
                    verified_states = np.array([1 if formula != '[false]' else -1 for formula in state])
                else:
                    verified_states = np.array([1 if formula != '[false]' else -1 for formula in state])
                    raise NotImplementedError
                return np.sum((np.multiply(verified_states, sel_probs)))

            elif force_terminal:
                verified_states = np.array([1 if (IsSafe(json.loads(formula))[0] and formula!='[false]') or formula == '[true]' else -1 for formula in state])
                return np.sum(np.multiply(verified_states, sel_probs))

            else:
                return 0
        else:
            raise Exception('Dimension mismatch between probabilities and state length')
    return Reward


def CreateReward_min_regret(probs):
    #note that the probs must be marginal probabilities of all formulas. The state description might include fewer states
    #Thus np.sum(probs) = 1
    #and len(probs) == len(state)

    #This should return a function of the state that will generate the reward for entering that state. The max reward is 1
    #The minimum possible reward is -1
    '''Deprecated: Use CreateReward instead'''

    def Reward(state, force_terminal=False):

        if len(probs) >= len(state):
            #Select the probabilisties of the states being considered
            sel_probs = np.array(probs[0:len(state)])
            sel_probs = sel_probs/np.sum(sel_probs)
            #Check if the state is a reward giving state
            if IsTerminalState(state):
                #select the non-falsified formula
                verified_states = np.array([1 if formula != '[false]' else -1 for formula in state])
                return np.sum((np.multiply(verified_states, sel_probs)))
            elif force_terminal:
                verified_states = np.array([1 if (IsSafe(json.loads(formula))[0] and formula!='[false]') else -5 for formula in state])
                return np.sum((np.multiply(verified_states, sel_probs)))
            else:
                return 0
        else:
            raise Exception('Dimension mismatch between probabilities and state length')
    return Reward


def FindAllProgressions_single_formula(formula):

    queue = deque([formula])
    visited = [formula]
    edges = {}
    progression_states = {}
    progression_states[json.dumps(formula)] = 0

    while queue:

        new_formula = queue.pop()
        vocabulary = GetVocabulary(new_formula)
        truth_assignments = get_all_truth_assignments(vocabulary)

        for truth_assignment in truth_assignments:
            progressed_formula = ProgressSingleTimeStep(new_formula, truth_assignment)
            edge = (json.dumps(new_formula), json.dumps(progressed_formula))
            if edge not in edges:
                edges[edge] = []
            edges[edge].append(truth_assignment)

            if progressed_formula not in visited:
                visited.append(progressed_formula)
                progression_states[json.dumps(progressed_formula)]=len(progression_states)
                queue.appendleft(progressed_formula)

    edge_tuples = []
    for edge in edges:
        edge_tuples.append((json.loads(edge[0]), json.loads(edge[1]), edges[edge]))
    return progression_states, edge_tuples




def VisualizeProgressionStates(progression_states, edge_tuples, RewardFun, single_formula = False, terminal_states = [],
                               colormap='reward', prog = 'dot'):

    G = nx.DiGraph()
    colors = {}
    for node in progression_states:
        G.add_node(progression_states[node])
        if colormap == 'terminal':
            colors[progression_states[node]] = 1 if node in terminal_states else 0
        elif colormap == 'reward':
            colors[progression_states[node]] = RewardFun(node, force_terminal=True)
        else:
            colors[progression_states[node]] = 0 #All nodes have the same color
    for edge in edge_tuples:
        e = (json.dumps(edge[0]), json.dumps(edge[1])) if single_formula else edge
        G.add_edge(progression_states[e[0]], progression_states[e[1]])

    colors = [colors[node] for node in G.nodes()]
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog=prog)
    nx.draw_networkx(G, pos, with_label=True, node_color = colors, cmap = 'coolwarm_r', vmin=-1.2, vmax=1.2)
    return G, colors


def IsTerminalState(state):
    return reduce(lambda memo, formula: memo and IsTerminal(json.loads(formula)), state, True)

def IsTerminal(formula):
    return json.dumps(formula) in set([json.dumps([True]),json.dumps([False]), json.dumps(['true']), json.dumps(['false'])]) or IsSafe(formula)[0]


def FindTerminalStates_single_formula(progression_states):
    terminal_states = [state for state in progression_states if IsTerminal(json.loads(state))]
    return terminal_states

def FindTerminalStates(progression_states):
    terminal_states = []
    for state in progression_states:
        if reduce(lambda memo, formula: memo and IsTerminal(json.loads(formula)), state, True):
            terminal_states.append(state)
    return terminal_states

if __name__ == '__main__':
    
    formula = ['and',
     ['G', ['not', ['W4']]],
     ['G', ['not', ['W0']]],
     ['F', ['W1']],
     ['F', ['W2']],
     ['F', ['W3']],
     ['U', ['not', ['W2']], ['W1']],
     ['U', ['not', ['W4']], ['W3']]]
    
    spec_fsm = SpecificationFSM([formula],[1])

    
    '''
  

    PathToDataFile = ''
    SampleSignal = Constants.ImportSampleData(PathToDataFile)
    TraceSlice = GetTraceSlice(SampleSignal,0)
    Formulas, Prob = Constants.ImportCandidateFormulas()
    idx = np.argsort(Prob)[::-1]
    Formulas_synth = np.array(Formulas)[idx]
    Probs_synth = np.array(Prob)[idx]
    ProgressedFormulas_synth = np.array([ProgressSingleTimeStep(formula, TraceSlice) for formula in Formulas_synth])

    SMDP = SpecificationFSM(ProgressedFormulas_synth, Prob, reward_type = 'chance_constrained', risk_level = 0.2)
    G,colors = SMDP.visualize(colormap = 'reward')
    '''

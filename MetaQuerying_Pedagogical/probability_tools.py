
#from pedagogical_demo import *
from puns.SpecificationFSMTools import *
from formula_utils import *
from scipy.stats import entropy
from scipy.special import softmax
import json

def compute_online_bsi_update(state, specification_fsm: SpecificationFSM, label, n_threats = 5, n_waypoints = 5):
    logprobs = np.log(specification_fsm._partial_rewards)

    #for each state in the FSM
    for (i,formula) in enumerate(state):
        formula = json.loads(formula)
        #Check if the formula is satisfied

        sat_check = (IsSafe(formula)[0] and formula != [False]) or formula == [True]
        factor = likelihood_factor(formula, label, sat_check, n_threats, n_waypoints)
        logprobs[i] = logprobs[i] + factor

    #the log probs should now be updated and unnormalized
    new_probs = softmax(logprobs)
    return {'formulas': specification_fsm._formulas, 'probs': new_probs}


def likelihood_factor(formula, label, sat_check, n_threats=5, n_waypoints=5):
    if formula[0] == 'and':
        n_conjuncts = len(formula[1::])
    else:
        n_conjuncts = 1

    if label:
        if sat_check:
            factor = np.log(2)*(n_conjuncts)
        else:
            factor = -4*np.log(2)*(n_threats + n_waypoints + 0.5*(n_waypoints)*(n_waypoints-1))
    else:
        if sat_check:
            factor = -4*np.log(2)*(n_threats + n_waypoints + 0.5*(n_waypoints)*(n_waypoints-1))
        else:
            factor = 0
    return factor

def compute_new_entropy(state, specification_fsm:SpecificationFSM, label, n_threats = 5, n_waypoints = 5):
    #take log of all probabilities and convert to a numpy array
    logprobs = np.log(specification_fsm._partial_rewards)

    #for each state in the FSM
    for (i,formula) in enumerate(state):
        formula = json.loads(formula)
        #Check if the formula is satisfied

        sat_check = (IsSafe(formula)[0] and formula != [False]) or formula == [True]
        factor = likelihood_factor(formula, label, sat_check, n_threats, n_waypoints)
        logprobs[i] = logprobs[i] + factor

    #the log probs should now be updated and unnormalized
    new_probs = softmax(logprobs)
    return entropy(new_probs)

def compute_expected_entropy_gain(state, specification_fsm, n_threats=5, n_waypoints=5):

    current_entropy = entropy(specification_fsm._partial_rewards)
    reward_func = CreateReward(specification_fsm._partial_rewards)
    p_true = 0.5*(reward_func(state, force_terminal = True)) + 0.5

    p_false = 1-p_true

    true_entropy = compute_new_entropy(state, specification_fsm, True, n_threats, n_waypoints)
    false_entropy = compute_new_entropy(state, specification_fsm, False, n_threats, n_waypoints)

    expected_entropy = p_true*true_entropy + p_false*false_entropy

    return current_entropy - expected_entropy

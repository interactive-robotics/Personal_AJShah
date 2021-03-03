#from query_strategy import *
from pedagogical_demo import *



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

def compute_expected_entropy_gain_demonstrations(specification_fsm, pedagogical = True, selectivity = None, n_threats=5, n_waypoints=5, debug=False):
    if pedagogical:
        if selectivity == None:
            return compute_expected_entropy_gain_pedagogical(specification_fsm, n_theats, n_waypoints)
        else:
            return compute_expected_entropy_gain_noisy_pedagogical(specification_fsm, selectivity, n_threats, n_waypoints)
    else:
        return compute_expected_entropy_gain_demonstrations_independent(specification_fsm, n_threats, n_waypoints)


    return expected_entropy_gain

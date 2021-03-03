from query_strategy import *



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

def compute_expected_entropy_gain_demonstrations(specification_fsm, n_threats=5, n_waypoints=5, debug=False):

    states = specification_fsm.states2id.keys()
    current_entropy = entropy(specification_fsm._partial_rewards)

    expected_entropies = [compute_new_entropy(state, specification_fsm, True,
    n_threats, n_waypoints) for state in states]

    expected_entropies = current_entropy - np.array(expected_entropies)

    #for each formula construct set of accepting states
    accepting_states = {}

    for (i,formula) in tqdm(list(enumerate(specification_fsm._formulas))):
        accepting_states[json.dumps(formula)] = list()
        for state in states:
            if IsSafe(json.loads(state[i]))[0] and json.loads(state[i]) != [False] or json.loads(state[i]) == [True]:
                #add state to the accepting states list
                accepting_states[json.dumps(formula)].append(state)

    #start with expected entropy gain 0
    expected_entropy_gain = 0
    p_state = {}

    #for all states, for all formulas compute P(state | formula) evenly divided
    #among number of accepting state if the state is an accepting state for that formula

    for (i,state) in tqdm(list(enumerate(states))):
        for (j,formula) in enumerate(specification_fsm._formulas):
            state_entropy = expected_entropies[i]
            p_state[state] = 0
            if state in accepting_states[json.dumps(formula)]:
                p_state_given_formula = 1/(len(accepting_states[json.dumps(formula)]))
                p_formula = specification_fsm._partial_rewards[j]
                p_state[state] = p_state[state] + p_state_given_formula*p_formula
                increment = state_entropy*p_state_given_formula*p_formula
                expected_entropy_gain = expected_entropy_gain + increment

    if debug:
        return {
        'accepting_states': accepting_states,
        'formulas': specification_fsm._formulas,
        'entropy_gains': expected_entropies,
        'states': states,
        'return_val': expected_entropy_gain,
        'p_state': p_state
        }
    return expected_entropy_gain

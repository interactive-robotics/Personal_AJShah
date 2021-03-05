# from Auto_Eval_Active import *
from formula_utils import compare_formulas, compare_distribution
from probability_tools import *
from query_selection import *
import networkx as nx
from tqdm import tqdm
from puns.utils import IsSafe
import json

def create_pedagogical_demo(ground_truth, MDP, selectivity = None, n_threats = 0, non_terminal = True, verbose = True):

    #Identify desired state in the current FSM
    desired_state, bread_crumb_states = identify_pedagogical_state(ground_truth, MDP.specification_fsm, selectivity)

    #Recompile the spec_fsm with the new reward`
    spec_fsm2 = recompile_reward_function(MDP.specification_fsm, desired_state, bread_crumb_states)
    for state_id in bread_crumb_states:
        if spec_fsm2.id2states[state_id] in spec_fsm2.terminal_states:
            spec_fsm2.terminal_states.remove(spec_fsm2.id2states[state_id])
    if non_terminal:
        spec_fsm2.terminal_states.append(desired_state)

    # Re-define MDP and learning agent
    MDP2 = SpecificationMDP(spec_fsm2, MDP.control_mdp)
    agent = QLearningAgent(MDP2)

    # Train learning agent to produce a query
    agent.explore(episode_limit = 5000, action_limit = 1000000, verbose = verbose)
    eval_agent = ExplorerAgent(MDP2, input_policy = agent.create_learned_softmax_policy(0.001))

    # Generate a query with the trained agent and visualize query
    eval_agent.explore(episode_limit = 1)
    #_ = eval_agent.visualize_exploration()

    # Create proposition trace slices
    episode_record = eval_agent.episodic_record[0]
    trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
    trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))

    #Ensure that the trace slices are correct with respect to the ground truth formula
    signal = create_signal(trace_slices)
    label = Progress(ground_truth, signal)[0]

    if not label:
        #Return an independent sampled demonstrations
        specification_fsm = SpecificationFSM(formulas=[ground_truth], probs = [1])
        control_mdp = MDP.control_mdp
        MDP2 = SpecificationMDP(specification_fsm, control_mdp)

        q_agent = QLearningAgent(MDP2)
        print('Training ground truth demonstrator')
        q_agent.explore(episode_limit = 5000, verbose=verbose, action_limit = 1000000)
        eval_agent = ExplorerAgent(MDP2, input_policy=q_agent.create_learned_softmax_policy(0.005))
        print('\n')
        eval_agent.explore(episode_limit = 1)

        episode_record = eval_agent.episodic_record[0]
        trace_slices = [MDP2.control_mdp.create_observations(record[0][1]) for record in episode_record]
        trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))

        desired_state = None

    return {'trace': trace_slices, 'agent': eval_agent, 'desired_state': desired_state}


''' ##################### State Identification #####################'''

def identify_pedagogical_state(ground_truth, prior_specification_fsm, selectivity = None, n_threats = 5, n_waypoints = 5):

    if selectivity == None:
        return identify_pedagogical_state_optimal(ground_truth, prior_specification_fsm, n_threats, n_waypoints)
    else:
        return identify_noisy_pedagogical_state(ground_truth, prior_specification_fsm, n_threats, n_waypoints)

def identify_pedagogical_state_optimal(ground_truth, prior_specification_fsm, n_threats = 5, n_waypoints = 5, debug = False):

    cross_entropies = []
    states = list(prior_specification_fsm.states2id.keys())

    for state in states:
        new_dist = compute_online_bsi_update(state, prior_specification_fsm, True, n_threats = n_threats, n_waypoints = n_waypoints)
        cross_entropies.append(compute_updated_cross_entropy(ground_truth, new_dist))

    state_idx = np.argmin(cross_entropies)
    desired_state = states[state_idx]

    path_to_desired_state = nx.all_simple_paths(prior_specification_fsm.graph, 0, prior_specification_fsm.states2id[desired_state])
    bread_crumb_states = set([l for sublists in path_to_desired_state for l in sublists]) - set([prior_specification_fsm.states2id[desired_state]])

    if debug:
        return {'desired_state': desired_state, 'breadcrumbs': bread_crumb_states, 'states': states, 'cross_entropies': cross_entropies}
    else:
        return desired_state, bread_crumb_states

def identify_noisy_pedagogical_state(ground_truth, prior_specification_fsm, selectivity = 5, n_threats = 5, n_waypoints= 5,  debug = False):
    #Uses noise pedagogical sampling to identify the next state, 0 is non-pedagogical, \infty represents perfect sample
    formula_probs = []
    states = list(prior_specification_fsm.states2id.keys())
    allowed_states = []

    for state in states:
        new_dist = compute_online_bsi_update(state, prior_specification_fsm, True)
        if is_formula_satisfied_in_state(ground_truth, state, prior_specification_fsm):
            allowed_states.append(state)
            formula_probs.append(get_formula_probability(ground_truth, new_dist))

    if prior_specification_fsm.id2states[0] not in allowed_states:
        allowed_states.append(prior_specification_fsm.id2states[0])
        new_dist = compute_online_bsi_update(prior_specification_fsm.id2states[0], prior_specification_fsm, True, n_threats = n_threats, n_waypoints = n_waypoints)
        formula_probs.append(get_formula_probability(ground_truth, new_dist))

    state_probs = np.power(formula_probs, selectivity)/np.sum(np.power(formula_probs, selectivity))
    desired_state_idx = np.random.choice(len(allowed_states), p = state_probs)
    desired_state = allowed_states[desired_state_idx]
    #print(selected_state_idx)

    #desired_state = states[selected_state_idx]

    path_to_desired_state = nx.all_simple_paths(prior_specification_fsm.graph, 0, prior_specification_fsm.states2id[desired_state])
    bread_crumb_states = set([l for sublists in path_to_desired_state for l in sublists]) - set([prior_specification_fsm.states2id[desired_state]])

    if debug:
        return {'desired_state': desired_state, 'breadcrumbs': bread_crumb_states, 'allowed_states': allowed_states, 'formula_probs': formula_probs, 'state_probs': state_probs}
    else:
        return desired_state, bread_crumb_states

'''##################### Expected Information Gain Computation ###################'''

def compute_expected_entropy_gain_demonstrations(specification_fsm, pedagogical = True, selectivity = None, n_threats=5, n_waypoints=5, debug=False):
    if pedagogical:
        if selectivity == None:
            return compute_expected_entropy_gain_pedagogical(specification_fsm, n_threats, n_waypoints)
        else:
            return compute_expected_entropy_gain_noisy_pedagogical(specification_fsm, selectivity, n_threats, n_waypoints)
    else:
        return compute_expected_entropy_gain_demonstrations_independent(specification_fsm, n_threats, n_waypoints)

def compute_expected_entropy_gain_noisy_pedagogical(specification_fsm, selectivity = 5, n_threats = 5, n_waypoints = 5, debug = False):
    current_entropy = entropy(specification_fsm._partial_rewards)
    entropy_gains = []
    expected_entropy_gain = 0
    states = list(specification_fsm.states2id.keys())

    new_dists = [compute_online_bsi_update(state, specification_fsm, True, n_threats, n_waypoints) for state in states]
    state_entropies = [entropy(dist['probs']) for dist in new_dists]

    allowed_states = []
    formula_probs = []
    selected_state_entropies = []

    for i in tqdm(range(len(specification_fsm._formulas))):
        formula = specification_fsm._formulas[i]
        p_formula = specification_fsm._partial_rewards[i]

        old_dist = specification_fsm._partial_rewards

        allowed_states.append([])
        formula_probs.append([])
        selected_state_entropies.append([])

        for (state, new_dist, state_entropy) in zip(states, new_dists, state_entropies):
            progressed_formula = json.loads(state[i])
            sat_check = (IsSafe(progressed_formula)[0] and progressed_formula != [False]) or progressed_formula == [True]
            if sat_check:
                allowed_states[i].append(state)
                formula_probs[i].append(new_dist['probs'][i])
                selected_state_entropies[i].append(state_entropy)

        if len(allowed_states[i]) > 0:
            temp = np.power(formula_probs[i], selectivity)
            state_probs = temp/np.sum(temp)
            increment = current_entropy - np.dot(selected_state_entropies[i], state_probs)
        else:
            increment = 0

        expected_entropy_gain = expected_entropy_gain + p_formula*increment

    if debug:
        return {'expected_entropy_gain': expected_entropy_gain, 'formulas': specification_fsm._formulas, 'allowed_states': allowed_states, 'formula_probs': formula_probs, 'selected_state_entropies': selected_state_entropies}
    else:
        return expected_entropy_gain

def compute_expected_entropy_gain_pedagogical(specification_fsm, n_threats = 5, n_waypoints = 5, debug = False):

    current_entropy = entropy(specification_fsm._partial_rewards)
    entropy_gains = []
    expected_entropy_gain = 0
    states = list(specification_fsm.states2id.keys())

    new_dists = [compute_online_bsi_update(state, specification_fsm, True, n_threats, n_waypoints) for state in states]
    state_entropies = [entropy(dist['probs']) for dist in new_dists]

    for i in tqdm(range(len(specification_fsm._formulas))):
        formula = specification_fsm._formulas[i]
        p_formula = specification_fsm._partial_rewards[i]

        cross_entropies = [-np.log(new_dist['probs'][i]) for new_dist in new_dists] #because these are the same formulas
        pedagogical_state_idx = np.argmin(cross_entropies)
        pedagogical_state = states[np.argmin(cross_entropies)]
        state_entropy = state_entropies[pedagogical_state_idx]
        pedagogical_entropy_gain = current_entropy - state_entropy
        entropy_gains.append(pedagogical_entropy_gain)

        expected_entropy_gain = expected_entropy_gain + pedagogical_entropy_gain*p_formula


    if debug:
        return {'expected_entropy_gain': expected_entropy_gain, 'entropy_gain': entropy_gains, 'formulas': specifications_fsm._formulas}
    else:
        return expected_entropy_gain


def compute_expected_entropy_gain_demonstrations_independent(specification_fsm, n_threats=5, n_waypoints=5, debug=False):
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

'''##################### Expected Model Change ###################'''

def compute_expected_model_change_demonstrations(spec_fsm, pedagogical=True, selectivity=None, n_threats=5, n_waypoints=5):
    if pedagogical:
        if selectivity == None:
            return compute_expected_model_change_optimal(spec_fsm, n_threats, n_waypoints)
        else:
            return compute_expected_model_change_noisy(spec_fsm, selectivity, n_threats, n_waypoints)
    else:
        return compute_expected_model_change_independent(spec_fsm, n_threats, n_waypoints)


def compute_expected_model_change_independent(spec_fsm:SpecificationFSM, n_threats=5, n_waypoints=5, debug=False):
    states = list(spec_fsm.states2id.keys())
    old_probs = spec_fsm._partial_rewards
    new_dists = [compute_online_bsi_update(state, spec_fsm, True) for state in states]
    model_changes = [jensenshannon(old_probs, d['probs']) for d in new_dists]
    expected_model_change = 0

    allowed_states = []
    state_probs = []
    selected_state_model_changes = []

    for i in tqdm(range(len(spec_fsm._formulas))):

        formula = specification_fsm._formulas[i]
        p_formula = specification_fsm._partial_rewards[i]
        old_dist = specification_fsm._partial_rewards

        allowed_states.append([])
        #state_probs.append([])
        selected_state_model_changes.append([])

        for (state, new_dist, state_model_change) in zip(states, new_dists, model_changes):
            progressed_formula = json.loads(state[i])
            sat_check = (IsSafe(progressed_formula)[0] and progressed_formula != [False]) or progressed_formula == [True]
            if sat_check:
                allowed_states[i].append(state)
                #formula_probs[i].append(new_dist['probs'][i])
                selected_state_model_changes[i].append(state_model_change)

        if len(allowed_states[i]) > 0:
            state_probs.append(np.ones(len(allowed_states[i]))/len(allowed_states[i]))
            increment = np.dot(state_probs[i], selected_state_model_changes[i])
        else:
            increment = 0

        expected_model_change = expected_model_change + p_formula*increment

    if debug:
        return {'expected_model_change': expected_model_change,
                'allowed_states': allowed_state,
                'state_probs': state_probs,
                'selected_model_changes': selected_model_changes,
                }
    else:
        return expected_model_change


def compute_expected_model_change_optimal(spec_fsm:SpecificationFSM, n_threats=5, n_waypoints=5, debug=False):
    states = list(spec_fsm.states2id.keys())
    old_probs = spec_fsm._partial_rewards
    new_dists = [compute_online_bsi_update(state, spec_fsm, True) for state in states]
    model_changes = [jensenshannon(old_probs, d['probs']) for d in new_dists]
    expected_model_change = 0

    #allowed_states = []
    #state_probs = []
    #selected_state_model_changes = []
    formula_model_changes = []

    for i in tqdm(range(len(spec_fsm._formulas))):
        p_formula = old_probs[i]
        formula = spec_fsm._formulas[i]

        cross_entropies = [-np.log(new_dist['probs'][i]) for new_dist in new_dists] #because these are the same formulas
        pedagogical_state_idx = np.argmin(cross_entropies)
        pedagogical_state = states[np.argmin(cross_entropies)]
        formula_model_change = model_changes[pedagogical_state_idx]
        formula_model_changes.append(formula_model_change)

        expected_model_change = expected_model_change + p_formula*formula_model_change

    if debug:
        return {'expected_model_change': expected_model_change,
                'model_changes': state_model_changes,
                'states': states,
                'formula_model_changes': formula_model_changes,
                'formulas': spec_fsm._formulas}
    else:
        return expected_model_change

def compute_expected_model_change_noisy(spec_fsm:SpecificationFSM, selectivity = 5, n_threats=5, n_waypoints=5, debug=False):
    current_entropy = entropy(spec_fsm._partial_rewards)
    old_probs = spec_fsm._partial_rewards
    expected_entropy_gain = 0
    states = list(spec_fsm.states2id.keys())

    new_dists = [compute_online_bsi_update(state, spec_fsm, True, n_threats, n_waypoints) for state in states]
    state_model_changes = [jensenshannon(old_probs, d['probs']) for d in new_dists]

    allowed_states = []
    formula_probs = []
    selected_model_changes = []

    for i in tqdm(range(len(spec_fsm._formulas))):
        formula = spec_fsm._formulas[i]
        p_formula = spec_fsm._partial_rewards[i]

        old_dist = spec_fsm._partial_rewards

        allowed_states.append([])
        formula_probs.append([])
        selected_model_changes.append([])

        for (state, new_dist, state_model_change) in zip(states, new_dists, state_model_changes):
            progressed_formula = json.loads(state[i])
            sat_check = (IsSafe(progressed_formula)[0] and progressed_formula != [False]) or progressed_formula == [True]
            if sat_check:
                allowed_states[i].append(state)
                formula_probs[i].append(new_dist['probs'][i])
                selected_model_changes[i].append(state_model_change)

        if len(allowed_states[i]) > 0:
            temp = np.power(formula_probs[i], selectivity)
            state_probs = temp/np.sum(temp)
            increment = np.dot(selected_model_changes[i], state_probs)
        else:
            increment = 0

        expected_entropy_gain = expected_entropy_gain + p_formula*increment

    if debug:
        return {'expected_entropy_gain': expected_entropy_gain, 'formulas': specification_fsm._formulas, 'allowed_states': allowed_states, 'formula_probs': formula_probs, 'selected_model_changes': selected_model_changes}
    else:
        return expected_entropy_gain



'''##################### Utility Functions ###################'''

def compute_updated_cross_entropy(formula, new_dist):

    similarities = [compare_formulas(formula, form) for form in new_dist['formulas']]
    most_similar_idx = np.argmax(similarities)
    return -np.log(new_dist['probs'][most_similar_idx])

def get_formula_probability(formula, new_dist):
    similarities = [compare_formulas(formula, form) for form in new_dist['formulas']]
    most_similar_idx = np.argmax(similarities)
    return new_dist['probs'][most_similar_idx]

def is_formula_satisfied_in_state(formula, state, spec_fsm):
    similarities = [compare_formulas(formula, form) for form in spec_fsm._formulas]
    most_similar_idx = np.argmax(similarities)
    #most_similar_formula= spec_fsm._formulas[most_similar_idx]
    progressed_formula = json.loads(state[most_similar_idx])
    sat_check = (IsSafe(progressed_formula)[0] and progressed_formula != [False]) or progressed_formula == [True]
    return sat_check

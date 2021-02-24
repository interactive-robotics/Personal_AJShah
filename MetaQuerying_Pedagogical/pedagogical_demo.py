# from Auto_Eval_Active import *
from formula_utils import compare_formulas, compare_distribution
from query_selection import *
import networkx as nx
#from tqdm import tqdm




def compute_updated_cross_entropy(formula, new_dist):

    similarities = [compare_formulas(formula, form) for form in new_dist['formulas']]
    most_similar_idx = np.argmax(similarities)
    #print(type(np))
    val = np.log(new_dist['probs'][most_similar_idx])
    
    return -val

def identify_pedagogical_state(ground_truth, prior_specification_fsm, debug = False):

    cross_entropies = []
    states = list(prior_specification_fsm.states2id.keys())

    for state in states:
        new_dist = compute_online_bsi_update(state, prior_specification_fsm, True, n_threats = 5, n_waypoints = 5)
        cross_entropies.append(compute_updated_cross_entropy(ground_truth, new_dist))

    state_idx = np.argmin(cross_entropies)
    desired_state = states[state_idx]

    path_to_desired_state = nx.all_simple_paths(prior_specification_fsm.graph, 0, prior_specification_fsm.states2id[desired_state])
    bread_crumb_states = set([l for sublists in path_to_desired_state for l in sublists]) - set([prior_specification_fsm.states2id[desired_state]])

    if debug:
        return{'desired_state': desired_state, 'bread_crumb_states': bread_crumb_states, 'cross_entropies': cross_entropies, 'states': states}

    return desired_state, bread_crumb_states



def create_pedagogical_demo(ground_truth, MDP, n_threats = 0, non_terminal = True, verbose = True):

    #Identify desired state in the current FSM
    desired_state, bread_crumb_states = identify_pedagogical_state(ground_truth, MDP.specification_fsm)

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

    return {'trace': trace_slices, 'agent': eval_agent, 'desired_state': desired_state}

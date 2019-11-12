import puns
from puns.utils import CreateSmallDinnerMDP,CreateDinnerMDP, CreateSmallDinnerMDP, Eventually, Order
from puns.ControlMDP import SmallTableMDP
from PUnSClient import *
from BSIClient import *
from utils import *
from DemoScript import *
import dill

def create_dinner_demonstrations(formula, nDemo):


    specification_fsm = SpecificationFSM(formulas=[formula], probs = [1])
    control_mdp = SmallTableMDP(0,5)
    MDP = SpecificationMDP(specification_fsm, control_mdp)

    q_agent = QLearningAgent(MDP)
    print('Training ground truth demonstrator')
    q_agent.explore(episode_limit = 5000, verbose=True, action_limit = 1000000)
    eval_agent = ExplorerAgent(MDP, input_policy=q_agent.create_learned_softmax_policy(0.005))
    print('\n')
    eval_agent.explore(episode_limit = nDemo)
    demos = []
    for record in eval_agent.episodic_record:
            new_demo = {}
            trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
            trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

            new_demo['trace'] = trace_slices
            new_demo['label'] = True
            demos.append(new_demo)
    return demos

def automated_server_trial_active(n_demo = 2, n_query = 3, formula = None):

    if not formula:
        formula = sample_ground_truth()

    demos = create_dinner_demonstrations(formula, n_demo)

    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    #Create MDP from the initial distribution
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    MDP = CreateSmallDinnerMDP(specfile)

    # Request queries
    for i in range(n_query):

        puns_request = create_puns_message(MDP, 'Active')
        agent = send_puns_request(puns_request)

        agent.explore(episode_limit = 1)
        #record = agent.episodic_record[0]
        episode_record = agent.episodic_record[0]
        trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
        trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))
        signal = create_signal(trace_slices)

        label = Progress(formula, signal)[0]
        prior_dist = {'formulas': MDP.specification_fsm._formulas, 'probs':MDP.specification_fsm._partial_rewards}
        active_query_message = create_active_message(trace_slices, label, prior_dist)
        dist = request_bsi_query(active_query_message)

        n_form = len(dist['support'])
        print(f'Received Query {i+1} results. Updating Distribution with {n_form} formulas')
        with open(specfile, 'w') as file:
            json.dump(dist, file)

        #Updating the MDP
        MDP = CreateSmallDinnerMDP(specfile)

    #The final distribution should have been written at this waypoints

    MDP = CreateSmallDinnerMDP(specfile)
    puns_request = create_puns_message(MDP, 'Puns')
    agent = send_puns_request(puns_request)
    print('Final Agent saved')
    print(formula)
    return

def automated_server_trial_random(n_demo = 2, n_query = 3, formula = None):

    if not formula:
        formula = sample_ground_truth()

    demos = create_dinner_demonstrations(formula, n_demo)

    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    # create an MDP from the initial distribution
    n_form = len(dist['probs'])
    print(f'Initial distribution has {n_form} formulas')
    MDP = CreateSmallDinnerMDP(specfile)

    # Request querying Agent
    for i in range(n_query):

        puns_request = create_puns_message(MDP, 'Random')
        agent = send_puns_request(puns_request)

        agent.explore(episode_limit = 1)
        episode_record = agent.episodic_record[0]
        trace_slices = [MDP.control_mdp.create_observations(record[0][1]) for record in episode_record]
        trace_slices.append(MDP.control_mdp.create_observations(episode_record[-1][2][1]))
        signal = create_signal(trace_slices)

        label = Progress(formula, signal)[0]
        prior_dist = {'formulas': MDP.specification_fsm._formulas,
        'probs': MDP.specification_fsm._partial_rewards}
        random_query_message = create_active_message(trace_slices, label, prior_dist)
        dist = request_bsi_query(random_query_message)

        n_form = len(dist['support'])
        print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
        with open(specfile,'w') as file:
            json.dump(dist, file)

        MDP = CreateSmallDinnerMDP(specfile)

    #The final distribution should have been written at this point

    puns_request = create_puns_message(MDP, 'Puns')
    #agent = send_puns_request(puns_request)
    agent = send_puns_request(puns_request)
    print('Final Agent saved')
    return

def real_active_trial(nQuery=3):

    formula = ['and']
    for i in range(5):
        formula.append(Eventually(f'W{i}'))
    formula.append(Order('W0','W1'))
    formula.append(Order('W0','W2'))
    formula.append(Order('W1','W2'))
    
    demos = create_dinner_demonstrations(formula, 2)
    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    #Create MDP from the initial distribution
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    MDP = CreateSmallDinnerMDP(specfile)

    for i in range(nQuery):

        #Get the active query agent

        puns_request = create_puns_message(MDP, 'Active')
        agent = send_puns_request(puns_request)
        #Lets assume that the demonstration has been written to './logs/query.pkl'
        

        text_label = input()
        label = True if lower(text_label)=='true' else False

        with open('logs/query.pkl','rb') as file:
            trace_slice = dill.load(file)
        prior_dist = {'formulas': MDP.specification_fsm._formulas,
        'probs': MDP.specification_fsm._partial_rewards}
        update_message = create_active_message(trace_slices, label, prior_dist)
        dist = request_bsi_query(update_message)
        n_form = len(dist['support'])
        print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
        with open(specfile,'w') as file:
            json.dump(dist, file)

        #Update the MDP definition
        MDP = CreateSmallDinnerMDP(specfile)









    return formula




if __name__ == '__main__':
    #automated_server_trial_active(n_demo = 2)
    #automated_server_trial_random(n_demo = 2)
    #print(real_active_trial())
    a=1

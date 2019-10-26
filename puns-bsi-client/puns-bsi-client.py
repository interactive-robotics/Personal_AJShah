import puns
from puns.utils import CreateSpecMDP,CreateDinnerMDP
from PUnSClient import *
from BSIClient import *
from utils import *
from DemoScript import *

def automated_server_trial(n_demo = 2, n_query = 5):

    formula = sample_ground_truth()
    demos = create_demonstrations(formula, n_demo)

    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    #Create MDP from the initial distribution
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    MDP = CreateSpecMDP(specfile, 0, 5)

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
        MDP = CreateSpecMDP(specfile, 0,5)

    #The final distribution should have been written at this waypoints

    MDP = CreateSpecMDP(specfile, 0,5)
    puns_request = create_puns_message(MDP, 'Puns')
    agent = send_puns_request(puns_request)
    print('Final Agent saved')

if __name__ == '__main__':
    automated_server_trial(n_demo = 2)

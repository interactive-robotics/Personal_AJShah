import puns
from puns.utils import CreateSmallDinnerMDP,CreateDinnerMDP, CreateSmallDinnerMDP, Eventually, Order
from puns.ControlMDP import SmallTableMDP
from PUnSClient import *
from BSIClient import *
from utils import *
from DemoScript import *
import dill
import os
import inputs

TEXT_HOST = 'localhost'
TEXT_PORT = 20000

def send_text(text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TEXT_HOST,TEXT_PORT))

        #print('Sending Demonstration Data')
        s.sendall(text.encode())

def create_dinner_demonstrations(formula, nDemo):


    specification_fsm = SpecificationFSM(formulas=[formula], probs = [1])
    control_mdp = SmallTableMDP()
    MDP = SpecificationMDP(specification_fsm, control_mdp)

    q_agent = QLearningAgent(MDP)
    print('Training ground truth demonstrator')
    q_agent.explore(episode_limit = 5000, verbose=True, action_limit = 1000000)
    eval_agent = ExplorerAgent(MDP, input_policy=q_agent.create_learned_softmax_policy(0.05))
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

def get_label_from_joystick():

    if not inputs.devices.gamepads: Exception('Please connect joystick')
    #send_text('Press Start to provide label')

    #Look for start button
    while True:
        event = inputs.get_gamepad()[-1]
        if event.code == 'BTN_START' and event.state == 0:
            send_text('Provide your label now: ')
            break
    while True:
        event = inputs.get_gamepad()[-1]
        if event.code == 'BTN_TR' and event.state == 0:
            label = True
            break
        if event.code == 'BTN_TL' and event.state == 0:
            label = False
            break
    #send_text(f'Your provided label is {label}')
    return label

def get_label_with_confirmation():
    send_text('Press Start to provide label')
    label1 = get_label_from_joystick()
    send_text(f'Provided label: {label1} \n\n Press start \n Confirm label {label1}')
    plt.pause(0.2)
    #send_text('Provide the same label again to continue')
    label2 = get_label_from_joystick()

    if label1 == label2:
        send_text(f'Label {label1} confirmed')
        plt.pause(0.2)
        return label1
    else:
        send_text('There was a label mismatch! Try Again when prompted')
        plt.pause(5)
        return get_label_with_confirmation()



def real_active_trial(nQuery=3, n_postdemo = 3, n_demo = 2):

    formula = ['and']
    for i in range(5):
        formula.append(Eventually(f'W{i}'))
    formula.append(Order('W0','W1'))
    formula.append(Order('W0','W2'))
    formula.append(Order('W1','W2'))

    demos = create_dinner_demonstrations(formula, n_demo)
    print(demos)

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

        send_text('Performing query demonstration. The robot is uncertain about this task execution')
        returnval = os.system('python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py')


        send_text('\nWhat is your label?')
        # text_label = input()

        label = get_label_from_joystick()
        new_text = f'Your confirmed label is {True}'
        send_text(new_text)

        with open('logs/query.pkl','rb') as file:
            trace_slices = dill.load(file)
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

    puns_request = create_puns_message(MDP, 'Puns')
    #agent = send_puns_request(puns_request)
    agent = send_puns_request(puns_request)
    print('Final Agent saved')

    print('\n Now showing what the robot has learned\n')
    for i in range(n_postdemo):
        print(f'Starting {i+1} of {n_postdemo} demonstration')
        returnval = os.system('python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py')

    return



if __name__ == '__main__':
    #automated_server_trial_active(n_demo = 2)
    #automated_server_trial_random(n_demo = 2)
    #real_active_trial()
    #get_label_from_joystick()
    send_text('Well hello')
    plt.pause(0.1)
    get_label_with_confirmation()
    
    

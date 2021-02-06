import puns
from puns.utils import CreateSmallDinnerMDP,CreateDinnerMDP, CreateSmallDinnerMDP, Eventually, Order
from puns.ControlMDP import SmallTableMDP
from PUnSClient import *
from BSIClient import *
from utils import *
from query_selection import *
import dill
import os
import inputs
import shutil
from gslides_utility import *

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

scope = ['https://spreadsheets.google.com/feeds']
cred = ServiceAccountCredentials.from_json_keyfile_name('GSheetsKey.json', scope)
gc = gspread.authorize(cred)


TEXT_HOST = 'localhost'
TEXT_PORT = 20000

def active_trial_remote(nQuery=3, n_postdemo = 3, n_demo = 2, trials = 1):


    clear_demonstrations()
    clear_logs()
    clear_dists()


    display_welcome()
    #send_text(f'Task A: Starting Learning Phase')
    plt.pause(5)

    for i in range(trials):
        returnval = 1
        while returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={i+1} --n-demo={n_demo} --trial'
            returnval = os.system(command)
            if returnval:
                print('Trying again, reset the table and reactivate robot')


    clear_demonstrations()



    demos = []
    for i in range(n_demo):
        #send_text(f'Learning Phase \n\n Collect demo {i+1} of {n_demo} \n\n Use the web form to teleoperate')
        #print('Press ENTER once complete')
        returnval = 1
        if returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={i+1} --n-demo={n_demo}'
            returnval = os.system(command)
            print('Trying again, reset the table and reactivate the robot')
        trace = parse_demonstration(i)
        new_demo = {}
        new_demo['trace'] = trace
        new_demo['label'] = True
        demos.append(new_demo)

    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist_0.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    #Create MDP from the initial distribution
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    MDP = CreateSmallDinnerMDP(specfile)

    for i in range(nQuery):

        #Get the active query agent

        display_waiting()
        puns_request = create_puns_message(MDP, 'Active')
        agent = send_puns_request(puns_request)
        #Lets assume that the demonstration has been written to './logs/query.pkl'

        display_query_waiting()
        #send_text('Learning Phase: Performing query demonstration.\n\n The robot is uncertain about this task execution \n\n Evaluate the robot\'s performance')
        returnval = 1
        if returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py query {i}'
            returnval = os.system(command)
            if returnval:
                print('Trying again, reset the table and reactivate the robot')

        display_query_assessment()
        #send_text('\nWhat is your label?')
        plt.pause(2)
        # text_label = input()

        label = get_latest_assessment()[0]
        #new_text = f'Your confirmed label is {label}'
        #send_text(new_text)
        assessment = 'Acceptable' if label else 'Unacceptable'
        display_query_confirmation(assessment)

        with open(f'logs/query_{i}.pkl','rb') as file:
            trace_slices = dill.load(file)
        prior_dist = {'formulas': MDP.specification_fsm._formulas,
        'probs': MDP.specification_fsm._partial_rewards}
        update_message = create_active_message(trace_slices, label, prior_dist)
        dist = request_bsi_query(update_message)
        n_form = len(dist['support'])
        print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
        specfile = f'Distributions/dist_{i+1}.json'
        with open(specfile,'w') as file:
            json.dump(dist, file)

        #Update the MDP definition
        MDP = CreateSmallDinnerMDP(specfile)

    display_waiting()
    puns_request = create_puns_message(MDP, 'Puns')
    #agent = send_puns_request(puns_request)
    agent = send_puns_request(puns_request)
    print('Final Agent saved')

    #send_text('Task B: Start Testing Phase\n')
    display_questionnaire()
    plt.pause(10)
    for i in range(n_postdemo):
        display_eval_slide(i+1, n_postdemo)
        #send_text(f'Testing phase\n\nShowing {i+1} of {n_postdemo} task executions')
        returnval = 1
        if returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py demo {i}'
            returnval = os.system(command)
            if returnval:
                print('Trying again: Reset the task and reactivate the robot')

    display_post()
    return

def Active_run(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3, query_strategy = 'info_gain'):
    clear_demonstrations()
    clear_logs()
    clear_dists()
    display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trials = trials)

    #Initialize the specification with batch BSI
    demos, dist = batch_bsi(n_demo = n_demo)

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each of the query request an active query and assessment and update the belief
    for i in range(n_query):
        dist, label, trace_slices, specfile = perform_active_query(i, MDP, query_strategy = query_strategy)
        #Recompile the MDP
        MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(n_postdemo)

    display_post()
    return

def Batch_run(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3):

    clear_demonstrations()
    clear_logs()
    clear_dists()
    display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trials = trials)

    #Initialize the specification with batch BSI
    demos, dist = batch_bsi(n_demo = n_demo)

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each of the query request an active query and assessment and update the belief
    for i in range(n_query):
        dist, label, trace_slices, specfile = incremental_demo_update(i, MDP, n_demo = n_demo)
        #Recompile the MDP
        MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(n_postdemo)

    display_post()
    return

def meta_selection_trials(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3):

    clear_demonstrations()
    clear_logs()
    clear_dists()
    display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trials = trials)

    #Initialize the specification with batch BSI
    demos, dist = batch_bsi(n_demo = n_demo)

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each query opportunity, decide whether to ask for a demonstration or perform a query
    for i in range(n_query):

        state, _ = identify_desired_state(MDP.specification_fsm, query_type = 'info_gain')
        query_entropy_gain = compute_expected_entropy_gain(state, MDP.specification_fsm)
        demonstration_entropy_gain = compute_expected_entropy_gain_demonstrations(MDP.specification_fsm)

        if demonstration_entropy_gain >= query_entropy_gain:
            #Ask for a demonstration

            dist, label, trace_slices, specfile = incremental_demp_update(i, MDP, n_demo = n_demo, query_strategy)
            MDP = CreateSmallDinnerMDP(specfile)
        else:
            #perform a query and ask for a label
            dist, label, trace_slices, specfile = perform_active_query(i. MDP, query_type = 'Active')
            MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(n_postdemo)

    display_post()
    return




''' %%%%%% High level functions for remote experiments %%%%%%% '''

def post_demo(n_postdemo = 3, MDP):
    display_waiting()
    puns_request = create_puns_message(MDP, 'Puns')
    #agent = send_puns_request(puns_request)
    agent = send_puns_request(puns_request)
    print('Final Agent saved')

    #send_text('Task B: Start Testing Phase\n')
    display_questionnaire()
    plt.pause(10)
    for i in range(n_postdemo):
        display_eval_slide(i+1, n_postdemo)
        #send_text(f'Testing phase\n\nShowing {i+1} of {n_postdemo} task executions')
        returnval = 1
        if returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py demo {i}'
            returnval = os.system(command)
            if returnval:
                print('Trying again: Reset the task and reactivate the robot')
    return


def trial_demonstration(n_trial = 1):
    for i in range(trials):
        returnval = 1
        while returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={i+1} --n-demo={n_demo} --trial'
            returnval = os.system(command)
            if returnval:
                print('Trying again, reset the table and reactivate robot')

def batch_bsi(n_demo = 2):
    '''returns the demonstrations and the updated posterior distribution after running batch BSI on server'''
    '''Also writes the appropriate file record for the subject'''
    clear_demonstrations()
    demos = []
    for i in range(n_demo):
        #send_text(f'Learning Phase \n\n Collect demo {i+1} of {n_demo} \n\n Use the web form to teleoperate')
        #print('Press ENTER once complete')
        returnval = 1
        if returnval:
            command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={i+1} --n-demo={n_demo}'
            returnval = os.system(command)
            print('Trying again, reset the table and reactivate the robot')
        trace = parse_demonstration(i)
        new_demo = {}
        new_demo['trace'] = trace
        new_demo['label'] = True
        demos.append(new_demo)

    send_data = create_batch_message([d['trace'] for d in demos])
    dist = request_bsi_query(send_data)
    specfile = 'Distributions/dist_0.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)

    return demos, dist, specfile

def perform_active_query(i, MDP, query_strategy = 'info_gain', query_type = 'Active'):
    display_waiting()
    puns_request = create_puns_message(MDP, query_type, query_strategy)
    agent = send_puns_request(puns_request)

    display_query_waiting()
    #send_text('Learning Phase: Performing query demonstration.\n\n The robot is uncertain about this task execution \n\n Evaluate the robot\'s performance')
    returnval = 1
    if returnval:
        command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py query {i}'
        returnval = os.system(command)
        if returnval:
            print('Trying again, reset the table and reactivate the robot')

    display_query_assessment()
    plt.pause(2)

    label = get_latest_assessment()[0]
    assessment = 'Acceptable' if label else 'Unacceptable'
    display_query_confirmation(assessment)

    with open(f'logs/query_{i}.pkl','rb') as file:
        trace_slices = dill.load(file)
    prior_dist = {'formulas': MDP.specification_fsm._formulas,
    'probs': MDP.specification_fsm._partial_rewards}
    update_message = create_active_message(trace_slices, label, prior_dist)
    dist = request_bsi_query(update_message)
    n_form = len(dist['support'])
    print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
    specfile = f'Distributions/dist_{i+1}.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)
    return dist, label, trace_slices, specfile

def incremental_demo_update(i, MDP, n_demo = 2):
    #Collect the demonstration
    returnval = 1
    demo_id = i + n_demo
    if returnval:
        command = f'python3.6 /media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts/run_teleop_agent_as_server.py --demo={demo_id} --n-demo={n_demo}'
        returnval = os.system(command)
        print('Trying again, reset the table and reactivate the robot')
    trace = parse_demonstration(demo_id)
    new_demo = {}
    new_demo['trace'] = trace
    new_demo['label'] = True

    #Now create the active query message
    prior_dist = {'formulas': MDP.specification_fsm._formulas,
    'probs': MDP.specification_fsm._partial_rewards}
    label = True
    update_message = create_active_message(trace, label, prior_dist)

    #Get response from server
    dist = request_bsi_query(update_message)
    print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
    specfile = f'Distributions/dist_{i+1}.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)
    return dist, label, trace_slices, specfile




    #Collect the query just like the batch demonstration




''' %%%%%%%%%% File Handling Helper Functions %%%%%%%%% '''

def clear_demonstrations():
    demofiles = [os.path.join('demos', f) for f in os.listdir('demos')]
    for f in demofiles:
        os.remove(f)

def clear_logs():
    logfiles = [os.path.join('logs',f) for f in os.listdir('logs')]
    for f in logfiles:
        os.remove(f)

def clear_dists():
    distfiles = [os.path.join('Distributions',f) for f in os.listdir('Distributions')]
    for f in distfiles:
        os.remove(f)

def record_subject_data(subject_id, execution_type):
    subjectpath = f'/home/shen/TableSetup_SubjectData/subject_{subject_id}_{execution_type}'
    if os.path.exists(subjectpath):
        print(f'Data for subject {subject_id} already exists. Please provide alternate subject number. Provide the same subject number to override')
        a = input()
        try:
            a  = int(a)
            if a == subject_id: print('Overwriting data')
        except:
            print('No subject id given exiting the function. Please run this again')
            return
        subject_id = a

    subjectpath = f'/home/shen/TableSetup_SubjectData/subject_{subject_id}_{execution_type}'
    try:
        shutil.rmtree(subjectpath)
    except:
        pass


    os.mkdir(subjectpath)

    #Copy over the final distribution
    os.mkdir(os.path.join(subjectpath, 'Distributions'))
    files = os.listdir('Distributions')
    for f in files:
        shutil.copyfile( os.path.join('Distributions', f) , os.path.join(subjectpath, 'Distributions',f))

    #Copy the logs
    os.mkdir(os.path.join(subjectpath, 'logs'))
    files = os.listdir('logs')
    for f in files:
        shutil.copyfile(os.path.join('logs', f), os.path.join(subjectpath, 'logs',f))

    #Copy the human demonstration logs
    os.mkdir(os.path.join(subjectpath, 'demos'))
    files = os.listdir('demos')
    for f in files:
        shutil.copyfile(os.path.join('demos',f), os.path.join(subjectpath,'demos',f))

    #Copy the final agent
    os.mkdir(os.path.join(subjectpath, 'Agents'))
    shutil.copyfile(os.path.join('Agents','Received_Agent.pkl'), os.path.join(subjectpath,'Agents','Final_Agent.pkl'))

def parse_demonstration(demo_id = 0):

    demofile = f'demos/demo_{demo_id}.txt'

    if os.path.exists(demofile):
        with open(demofile,'r') as file:
            lines = file.readlines()

        state_tuples = [tuple(json.loads(line)) for line in lines]
        cmdp = SmallTableMDP()
        trace_slices = [cmdp.create_observations(t) for t in state_tuples]
        return trace_slices

    else:
        print(f'Record demonstration {demo_id}')
        print('Press Enter when demonstration is recorded')
        input()
        return parse_demonstration(demo_id)


'''%%%%%%%% In Person UI and joystick helper functions %%%%%%%'''
def send_text(text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TEXT_HOST,TEXT_PORT))

        #print('Sending Demonstration Data')
        s.sendall(text.encode())

def get_label_from_joystick():

    if not inputs.devices.gamepads: Exception('Please connect joystick')
    #send_text('Press Start to provide label')

    #Look for start button
    while True:
        event = inputs.get_gamepad()[-1]
        if event.code == 'BTN_START' and event.state == 0:
            send_text('Ready to receive input now ')
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
    send_text(f'Provided label: {label1} \n\n Press Start \n Then confirm label: {label1}')
    plt.pause(0.2)
    #send_text('Provide the same label again to continue')
    label2 = get_label_from_joystick()

    if label1 == label2:
        send_text(f'Label confirmed')
        plt.pause(0.2)
        return label1
    else:
        send_text('There was a label mismatch!\n\n Try Again when prompted')
        plt.pause(5)
        return get_label_with_confirmation()


'''%%%%%%%% Google sheets API functions %%%%%%%'''
def checkdiff(previous_record, new_record):
    return len(previous_record) != len(new_record)

def get_current_record(typ = 'command'):
    if typ == 'command':
        workbook = gc.open_by_url('https://docs.google.com/spreadsheets/d/1-WHaUoXEJ5Ksw6TjscpBtoT7BiZd4kkmRiXDN8rbJQ0/edit?usp=sharing')
    else:
        workbook = gc.open_by_url('https://docs.google.com/spreadsheets/d/1yNtNTk-s18f_X5VnRmkLHFT2XPtoFVPhtSN5TN6YLY4/edit?usp=sharing')
    data = workbook.get_worksheet(0)
    return data.get_all_records()

def get_latest_assessment():

    previous_record = get_current_record('assessment')
    print('Waiting for google form response')
    while True:

        new_record = get_current_record('assessment')

        if checkdiff(previous_record, new_record):
            previous_record = new_record
            assessment = new_record[-1]['Assessment']
            print(f'Obtained assessment: {assessment}')
            if assessment == 'Acceptable':
                return (True, new_record)
            else:
                return (False, new_record)
        else:
            time.sleep(2)



''' %%%%%%% Demonstration Helper %%%%%%%%%%'''
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





if __name__ == '__main__':
    #automated_server_trial_active(n_demo = 2)
    #automated_server_trial_random(n_demo = 2)
    #send_text('Well Hello!')
    #plt.pause(3)
    #real_active_trial()
    #get_label_from_joystick()
    #send_text('Well hello')
    #plt.pause(0.1)
    send_text('Testing the joystick module')
    plt.pause(4)
    get_label_with_confirmation()

    active_trial(nQuery=2, n_demo = 3)
    record_subject_data(100,'Active')

    random_trial(nQuery = 2, n_demo = 3)
    record_subject_data(100,'Random')
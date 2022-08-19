import puns
from IPython import embed
from puns.utils import CreateSmallDinnerMDP,CreateDinnerMDP, CreateSmallDinnerMDP, Eventually, Order
from puns.ControlMDP import SmallTableMDP
from PUnSClient import *
from BSIClient import *
from utils import * #Do I really need this import?
from query_selection import *
from pedagogical_demo  import *
import dill
import os
import inputs
import shutil
#from gslides_utility import *
import signal

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

import rospy
from std_msgs.msg import String


### Removing authorization for google APIs
#scope = ['https://spreadsheets.google.com/feeds']
#cred = ServiceAccountCredentials.from_json_keyfile_name('GSheetsKey.json', scope)
#gc = gspread.authorize(cred)

#COMMAND_SERVER_SCRIPT_PATH = '/media/homes/demo/puns_demo/src/LTL_specification_MDP_control_MDP/scripts' #For Robbie-yuri demo computer
COMMAND_SERVER_SCRIPT_PATH = '/home/panda1/puns_demo/LTL_specification_MDP_control_MDP/scripts/' #For the 31 Franka computer
#COMMAND_SERVER_SCRIPT_PATH = '' Make sure to set this whenever you are using a new computer.
# TODO: Perhaps we can set up a constants file where all these paths are stored

SUBJECT_DATA_PATH = '/home/shen/TableSetup_SubjectData/' # For Robbit-yuri computer
SUBJECT_DATA_PATH = '' # Set this for installation to any new computer


AUTONOMOUS_SERVER = 'run_q_learning_agent_as_server_interactive.py'
TELEOP_SERVER = 'run_teleop_agent_as_server.py'


TEXT_HOST = 'localhost'
TEXT_PORT = 20000

#Write recoveries for all of them in the task file to recover from unexpected failures

active_query_ROS_msg = None


def Active_run(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3, query_strategy = 'uncertainty_sampling', k = 2):
    clear_demonstrations()
    clear_logs()
    clear_dists()
    #display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trial = trials)

    #Initialize the specification with batch BSI
    demos, dist, specfile = batch_bsi(n_demo = n_demo, demo_type = 'physical')

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each of the query request an active query and assessment and update the belief
    for i in range(n_query):
        dist, label, trace_slices, specfile = perform_active_query(i, MDP, query_strategy = query_strategy, k=k)
        #Recompile the MDP
        MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(MDP, n_postdemo)

    #display_post()
    return

def Batch_run(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3):

    clear_demonstrations()
    clear_logs()
    clear_dists()
    #display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trial = trials)

    #Initialize the specification with batch BSI
    demos, dist, specfile = batch_bsi(n_demo = n_demo)

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
    post_demo(MDP, n_postdemo)

    #display_post()
    return

def Meta_run(trials = 1, n_demo = 2, n_query = 3, n_postdemo = 3, pedagogical = True, selectivity = 0, meta_policy = 'info_gain', query_strategy = 'uncertainty_sampling', k = 2):

    clear_demonstrations()
    clear_logs()
    clear_dists()
    #display_welcome()
    plt.pause(5)

    #Run the trial demonstrations
    trial_demonstration(n_trial = trials)

    #Initialize the specification with batch BSI
    demos, dist, specfile = batch_bsi(n_demo = n_demo)

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each query opportunity, decide whether to ask for a demonstration or perform a query
    for i in range(n_query):

        # state, _ = identify_desired_state(MDP.specification_fsm, query_type = 'info_gain')
        # query_entropy_gain = compute_expected_entropy_gain(state, MDP.specification_fsm)
        # demonstration_entropy_gain = compute_expected_entropy_gain_demonstrations(MDP.specification_fsm)
        # print('Query expected gain: ', query_entropy_gain)
        # print('Demo expected gain: ', demonstration_entropy_gain)

        demo, demonstration_gain, query_gain = run_meta_policy(MDP.specification_fsm, meta_policy, query_strategy, pedagogical, selectivity)
        print('Demonstration Gain: ', demonstration_gain)
        print('Query Gain: ', query_gain)

        print('Demo' if demo else 'Query')

        if demo:
            #Ask for a demonstration
            dist, label, trace_slices, specfile = incremental_demo_update(i, MDP, n_demo)
            MDP = CreateSmallDinnerMDP(specfile)
        else:
            #perform a query and ask for a label
            dist, label, trace_slices, specfile = perform_active_query(i, MDP, query_type = 'Active', k=k)
            MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(MDP, n_postdemo)

    #display_post()
    return
# 220817: Based on Shen and Ankit's email about <question about puns> (see https://github.com/interactive-robotics/Personal_AJShah/blob/museum_demo/meta_client/failed_demos_for_debug/220817/notes.txt):
def Active_demo(n_demo = 3, n_query = 3, n_postdemo = 1, pedagogical = True, selectivity = 0, meta_policy = 'max_model_change', query_strategy = 'uncertainty_sampling', k=2):

    # Shen 220601: we clear demos after Meta_demo.
    # clear_demonstrations()

    clear_logs()
    clear_dists()
    #display_welcome()
    plt.pause(5)

    #Initialize specification with batch BSI
    demos, dist, specfile = batch_bsi(n_demo = n_demo, demo_type = 'physical')

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each query opportunity, decide whether to ask for a demonstration or perform a query
    for i in range(n_query):

        # 220817: Based on Shen and Ankit's email about <question about puns> (see https://github.com/interactive-robotics/Personal_AJShah/blob/museum_demo/meta_client/failed_demos_for_debug/220817/notes.txt):
        # demo, demonstration_gain, query_gain = run_meta_policy(MDP.specification_fsm, meta_policy, query_strategy, pedagogical, selectivity)
        demo = False

        if demo:
            #Ask for a demonstration
            dist, label, trace_slices, specfile = incremental_demo_update(i, MDP, n_demo, demo_type = 'physical')
            MDP = CreateSmallDinnerMDP(specfile)
        else:
            #perform a query and ask for a label
            dist, label, trace_slices, specfile = perform_active_query(i, MDP, query_type = 'Active', k=k)
            MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    post_demo(MDP, n_postdemo)

    #display_post()

    # Shen 220601: we clear demos after Meta_demo.
    clear_demonstrations()

    return


def Meta_demo(n_demo = 3, n_query = 3, n_postdemo = 1, pedagogical = True, selectivity = 0, meta_policy = 'max_model_change', query_strategy = 'uncertainty_sampling', k=2):

    # Shen 220601: we clear demos after Meta_demo.
    # clear_demonstrations()

    clear_logs()
    clear_dists()
    #display_welcome()
    plt.pause(5)

    #Initialize specification with batch BSI
    demos, dist, specfile = batch_bsi(n_demo = n_demo, demo_type = 'physical')

    #Initialize the MDP
    n_form = len(dist['probs'])
    print(f'Initial Batch distributions has {n_form} formulas')
    specfile = 'Distributions/dist_0.json'
    MDP = CreateSmallDinnerMDP(specfile)

    #For each query opportunity, decide whether to ask for a demonstration or perform a query
    for i in range(n_query):

        demo, demonstration_gain, query_gain = run_meta_policy(MDP.specification_fsm, meta_policy, query_strategy, pedagogical, selectivity)

        if demo:
            #Ask for a demonstration
            dist, label, trace_slices, specfile = incremental_demo_update(i, MDP, n_demo, demo_type = 'physical')
            MDP = CreateSmallDinnerMDP(specfile)
        else:
            #perform a query and ask for a label
            dist, label, trace_slices, specfile = perform_active_query(i, MDP, query_type = 'Active', k=k)
            MDP = CreateSmallDinnerMDP(specfile)

    #perform the evaluation trials
    #post_demo(MDP, n_postdemo)

    #display_post()

    # Shen 220601: we clear demos after Meta_demo.
    clear_demonstrations()

    return



''' %%%%%% High level functions for remote experiments %%%%%%% '''

def post_demo(MDP, n_postdemo = 3):
    #display_waiting()
    puns_request = create_puns_message(MDP, 'Puns')
    #agent = send_puns_request(puns_request)
    agent = send_puns_request(puns_request)
    print('Final Agent saved')

    #send_text('Task B: Start Testing Phase\n')
    #display_questionnaire()
    plt.pause(10)
    for i in range(n_postdemo):
        #display_eval_slide(i+1, n_postdemo)
        #send_text(f'Testing phase\n\nShowing {i+1} of {n_postdemo} task executions')
        returnval = 1
        while returnval:
            scriptfile = os.path.join(COMMAND_SERVER_SCRIPT_PATH, AUTONOMOUS_SERVER)
            command = f'python3 {scriptfile} demo {i}'
            returnval = os.system(command)

            # 220629: Shen added this, so that the script can be killed by ctrl+c, based on https://stackoverflow.com/questions/42693527/stop-an-infinite-while-loop-repeatedly-invoking-os-system
            if returnval == signal.SIGINT:
                print("You just hit ctrl+c, so exit.")
                exit()
            elif returnval:
                print('Trying again: Reset the task and reactivate the robot')
    return


def trial_demonstration(n_trial = 1):
    for i in range(n_trial):
        returnval = 1
        while returnval:
            scriptfile = os.path.join(COMMAND_SERVER_SCRIPT_PATH, TELEOP_SERVER)
            command = f'python3 {scriptfile} --demo={i+1} --n-demo={1} --trial'
            returnval = os.system(command)

            # 220629: Shen added this, so that the script can be killed by ctrl+c, based on https://stackoverflow.com/questions/42693527/stop-an-infinite-while-loop-repeatedly-invoking-os-system
            if returnval == signal.SIGINT:
                print("You just hit ctrl+c, so exit.")
                exit()
            elif returnval:
                print('Trying again, reset the table and reactivate robot')

def batch_bsi(n_demo = 2, demo_type = 'physical'):
    '''returns the demonstrations and the updated posterior distribution after running batch BSI on server'''
    '''Also writes the appropriate file record for the subject'''

    # Shen 220601: we clear demos after Meta_demo.
    # clear_demonstrations()

    demos = []
    for i in range(n_demo):
        #send_text(f'Learning Phase \n\n Collect demo {i+1} of {n_demo} \n\n Use the web form to teleoperate')
        #print('Press ENTER once complete')
        if demo_type == 'virtual': #Virtual demo type will no longer be supported once the google API dependency is removed

            returnval = 1
            while returnval:
                scriptfile = os.path.join(COMMAND_SERVER_SCRIPT_PATH, TELEOP_SERVER)
                command = f'python3 {scriptfile} --demo={i+1} --n-demo={n_demo}'
                returnval = os.system(command)

                # 220629: Shen added this, so that the script can be killed by ctrl+c, based on https://stackoverflow.com/questions/42693527/stop-an-infinite-while-loop-repeatedly-invoking-os-system
                if returnval == signal.SIGINT:
                    print("You just hit ctrl+c, so exit.")
                    exit()
                elif returnval:
                    print('Trying again, reset the table and reactivate the robot')

        trace = parse_demonstration(i) #The execution should pause at this step till demonstrations are recorded
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

def perform_active_query(i, MDP, query_strategy = 'info_gain', query_type = 'Active', k = 1):
    # 220819: Shen: adding ROS interface for getting feedback.
    global active_query_ROS_msg
    
    #display_waiting()
    puns_request = create_puns_message(MDP, query_type, query_strategy, k)
    agent = send_puns_request(puns_request)

    #display_query_waiting()
    #send_text('Learning Phase: Performing query demonstration.\n\n The robot is uncertain about this task execution \n\n Evaluate the robot\'s performance')
    returnval = 1
    while returnval:
        scriptfile = os.path.join(COMMAND_SERVER_SCRIPT_PATH, AUTONOMOUS_SERVER)
        command = f'python3 {scriptfile} query {i}'
        # python /home/panda1/puns_demo/LTL_specification_MDP_control_MDP/scripts/run_q_learning_agent_as_server_interactive.py query 0
        print(command)
        returnval = os.system(command)

        # 220629: Shen added this, so that the script can be killed by ctrl+c, based on https://stackoverflow.com/questions/42693527/stop-an-infinite-while-loop-repeatedly-invoking-os-system
        if returnval == signal.SIGINT:
            print("You just hit ctrl+c, so exit.")
            exit()
        elif returnval:
            print('Trying again, reset the table and reactivate the robot')

    #display_query_assessment()
    plt.pause(2)

    # label = get_latest_assessment()[0] # TODO This needs to be changed with whatever new assessment method is decided upon
    #You can replace this in the interim with the get_label_with_confirmation(), if you have an XBox controller.
    #It might work with any USB based controller but you will have to edit the get_label_from_joystick() function.

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    
    # 220819: Shen: adding ROS interface for getting feedback.
    # Acceptable: rostopic pub -1 /puns_feedback std_msgs/String "data: 'Acceptable'"
    # Unacceptable: rostopic pub -1 /puns_feedback std_msgs/String "data: 'Unacceptable'"
    # https://github.com/shenlirobot/museum_notes/blob/3cb847a5ce82d6bbc293f49c09045b1f806be22a/mit-museum/mitmuseum/demo_scripts/kitchentable/kt-feedback-y.sh#L18
    # https://github.com/shenlirobot/museum_notes/blob/3cb847a5ce82d6bbc293f49c09045b1f806be22a/mit-museum/mitmuseum/demo_scripts/kitchentable/kt-feedback-n.sh#L18
    rospy.Subscriber("/puns_feedback", String, perform_active_query_ROS_callback)
    rate = rospy.Rate(10) # 10hz
    rospy.sleep(1)
    print("Waiting for feedback ...")
    while not rospy.is_shutdown():
        if active_query_ROS_msg is None:
            rate.sleep()
        elif active_query_ROS_msg not in ["Acceptable", "Unacceptable"]:
            rate.sleep()
        else:
            break
    print("Receiving feedback="+str(active_query_ROS_msg))
    if active_query_ROS_msg == "Acceptable":
        label = True
    elif active_query_ROS_msg == "Unacceptable":
        label = False
    else:
        raise Exception("You should not be here!")
    active_query_ROS_msg = None
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    

    assessment = 'Acceptable' if label else 'Unacceptable'
    print(assessment + "\n\n")
    #display_query_confirmation(assessment)

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

def perform_active_query_ROS_callback(data):
    # 220819: Shen: adding ROS interface for getting feedback.
    global active_query_ROS_msg
    active_query_ROS_msg = data.data

def incremental_demo_update(i, MDP, n_demo = 2, demo_type = 'virtual'):
    #Collect the demonstration
    returnval = 1
    demo_id = i + n_demo
    if demo_type == 'virtual':
        while returnval:
            scriptfile = os.path.join(COMMAND_SERVER_SCRIPT_PATH, TELEOP_SERVER)
            command = f'python3 {scriptfile} --demo={demo_id} --n-demo={n_demo}'
            returnval = os.system(command)

            # 220629: Shen added this, so that the script can be killed by ctrl+c, based on https://stackoverflow.com/questions/42693527/stop-an-infinite-while-loop-repeatedly-invoking-os-system
            if returnval == signal.SIGINT:
                print("You just hit ctrl+c, so exit.")
                exit()
            elif returnval:
                print('Trying again, reset the table and reactivate the robot')
    else:
        #display_demo_intro(demo_id, n_demo)
        # 220819: Shen:
        raise Exception("You should not be here!")
    trace = parse_demonstration(demo_id) #The execution should pause here till the demonstrations is recorded
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
    n_form = len(dist['support'])
    print(f'Received Query {i+1} results. Updated distribution has {n_form} formulas')
    specfile = f'Distributions/dist_{i+1}.json'
    with open(specfile,'w') as file:
        json.dump(dist, file)
    return dist, label, trace, specfile

def run_meta_policy(spec_fsm:SpecificationFSM, meta_policy = 'info_gain', query_type = 'uncertainty_sampling', pedagogical = True, selectivity = None):
    query_state,_ = identify_desired_state(spec_fsm, query_type = query_type)
    if meta_policy == 'info_gain':
        query_gain = compute_expected_entropy_gain(query_state, spec_fsm)
        demonstration_gain = compute_expected_entropy_gain_demonstrations(spec_fsm, pedagogical, selectivity)
        #demo = True if demonstration_entropy_gain >= query_entropy_gain
    elif meta_policy == 'max_model_change':
        query_gain = compute_expected_model_change(query_state, spec_fsm)
        demonstration_gain = compute_expected_model_change_demonstrations(spec_fsm, pedagogical, selectivity)
    elif meta_policy == 'uncertainty_sampling':
        query_gain = -np.abs(spec_fsm.reward_function(query_state, force_terminal = True))
        demonstration_gain = -np.abs(compute_expected_reward(spec_fsm, pedagogical, selectivity))

    demo = True if demonstration_gain >= query_gain else False
    return demo, demonstration_gain, query_gain




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
    subjectpath = os.path.join(SUBJECT_DATA_PATH, f'subject_{subject_id}_{execution_type}')
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

    subjectpath = os.path.join(SUBJECT_DATA_PATH, f'subject_{subject_id}_{execution_type}')
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

        print([line for line in lines])
        state_tuples = [tuple(json.loads(line)) for line in lines]
        cmdp = SmallTableMDP()
        trace_slices = [cmdp.create_observations(t) for t in state_tuples]
        return trace_slices

    else:
        # Shen: 220601: we don't allow waiting for demos in this script.
        raise Exception("Please provide initial demos and run this again!")
        # print(f'Record demonstration {demo_id}')
        # print('Press Enter when demonstration is recorded')
        # input()
        # return parse_demonstration(demo_id)


'''%%%%%%%% In Person UI and joystick helper functions %%%%%%%'''
def send_text(text):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TEXT_HOST,TEXT_PORT))

        #print('Sending Demonstration Data')
        s.sendall(text.encode())

def get_label_from_joystick():
    #This uses a 2 step process. You press one button to prime the system to receive the label on the next press.
    #Then you use the next press to signal True or False
    #If you use anything other than an XBox controller you will need to change 'BTN_START','BTN_TR','BTN_TL' to the correct map.
    #For example to provide the label True, you will press start, then press the button for true

    if not inputs.devices.gamepads: Exception('Please connect joystick')
    #send_text('Press Start to provide label')

    #Look for start button
    while True:
        event = inputs.get_gamepad()[-1]
        if event.code == 'BTN_START' and event.state == 0:
            #send_text('Ready to receive input now ')
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
    # This function basically asks you to repeat the assessment twice and have it match.
    print('Press Start to provide label')
    label1 = get_label_from_joystick()
    print(f'Provided label: {label1} \n\n Press Start \n Then confirm label: {label1}')
    plt.pause(0.2)
    #send_text('Provide the same label again to continue')
    label2 = get_label_from_joystick()

    if label1 == label2:
        print(f'Label confirmed')
        plt.pause(0.2)
        return label1
    else:
        print('There was a label mismatch!\n\n Try Again when prompted')
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

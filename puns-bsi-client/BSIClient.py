from DemoScript import *
from utils import *
from puns.utils import CreateSpecMDP, Eventually, Order
from puns.SpecificationMDP import *
from puns.LearningAgents import QLearningAgent
from puns.Exploration import ExplorerAgent
import numpy as np
import dill

import os
import json
import socket
import time

HOST = 'ajshah.mit.edu'
PORT1 = 10050
#PORT2 = 10000

def request_bsi_query(data):

    data_string = dill.dumps(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT1))

        print('Sending Demonstration Data')
        s.sendall(data_string)
        s.sendall(b'DONE')

        print('Awaiting Reply ...')

        rec_data = b''
        while True:
            newdata = s.recv(1024)
            rec_data +=  newdata
            if not newdata: break
        print('Distribution Received\n\n')

    dist = dill.loads(rec_data)
    return dist

def create_active_message(trace, label, dist):
    prior_dist = {}
    prior_dist['support'] = dist['formulas'].tolist()
    prior_dist['probs'] = dist['probs'].tolist()

    demo = {}
    demo['trace'] = trace
    demo['label'] = label

    send_data = {}
    send_data['request_type'] = 'Active'
    send_data['demos'] = demo
    send_data['prior_dist'] = prior_dist
    return send_data



def create_batch_message(traces):

    demos = []
    for trace in traces:
        new_demo = {}
        new_demo['trace'] = trace
        new_demo['label'] = True
        demos.append(new_demo)

    send_data = {}
    send_data['request_type'] = 'Batch'
    send_data['demos'] = demos
    return send_data



def send_sample_batch_query():

    send_data = create_sample_batch_data()
    dist = request_bsi_query(send_data)
    return dist

def send_sample_active_query():
    send_data = create_sample_active_query()
    dist = request_bsi_query(send_data)
    return dist

def create_demonstrations(formula, nDemo):


    specification_fsm = SpecificationFSM(formulas=[formula], probs = [1])
    control_mdp = SyntheticMDP(0,5)
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

def create_sample_active_query():
    with open('Active_Run_0.pkl','rb') as file:
        data = dill.load(file)
    prior_dist = {}
    prior_dist['support'] = data['Distributions'][0]['formulas'].tolist()
    prior_dist['probs'] = data['Distributions'][0]['probs'].tolist()

    demo = {}
    demo['trace'] = data['Queries'][0]
    demo['label'] = False

    send_data = {}
    send_data['request_type'] = 'Active'
    send_data['demos'] = demo
    send_data['prior_dist'] = prior_dist

    return send_data


def create_sample_batch_data():
    ground_truth_formula = sample_ground_truth()
    demos = create_demonstrations(ground_truth_formula, 2)

    send_data = {}
    send_data['request_type'] = 'Batch'
    send_data['demos'] = demos
    data_string = dill.dumps(send_data)
    return send_data




#def send_sample_batch_query

if __name__ == '__main__':

    send_data = create_sample_active_query()
    dist = send_sample_active_query()
    dist = send_sample_batch_query()

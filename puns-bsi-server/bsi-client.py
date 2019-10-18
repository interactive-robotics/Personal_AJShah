from DemoScript import *
from utils import *
from puns.utils import CreateSpecMDP, Eventually, Order
from puns.SpecificationMDP import *
from puns.LearningAgents import QLearningAgent
from puns.Exploration import ExplorerAgent
from numpy.random import binomial
import numpy as np
from scipy.stats import entropy
from matplotlib.backends.backend_pdf import PdfPages
import dill
import auto_eval_params as params
import os
import json
import socket
import time

HOST = 'ajshah.mit.edu'
PORT1 = 10050
#PORT2 = 10000

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

def send_sample_batch_query():

    ground_truth_formula = sample_ground_truth()
    demos = create_demonstrations(ground_truth_formula, 2)

    send_data = {}
    send_data['request_type'] = 'Batch'
    send_data['demos'] = demos
    data_string = dill.dumps(send_data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT1))
        s.sendall(data_string)
        print('Data sent')
        s.close()
    time.sleep(2)
        
        #s.connect((HOST,PORT))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            try:
                print('Awaiting Reply...')
                s.connect((HOST,PORT1))
                print('connected')
                break
            except:
                time.sleep(2)
                continue
        rec_data = b""
        
        while True:
            #print('receiving')
            newdata = s.recv(1024)
            #print(newdata)
            rec_data += newdata
            if not newdata:
                break
        print('Distribution Received')
        
        #s.sendall(b'done')
        s.close()
    dist = dill.loads(rec_data)
    return dist

if __name__ == '__main__':

    dist = send_sample_batch_query()

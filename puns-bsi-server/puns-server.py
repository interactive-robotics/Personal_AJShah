import socket
import dill
import json
from DemoScript import *
from puns.SpecificationFSMTools import SpecificationFSM, CreateReward
from puns.SpecificationMDP import SpecificationMDP
import auto_eval_params as params
import os
import time

HOST = 'ajshah.mit.edu'
PORT = 10020

def decode_data(data):
    #try:
    data = dill.loads(data)
    # except:
    #     print('data not readable by dill: ', data)
    #     print('No action taken')
    return data

def train_puns(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
#    print('Recompiling MDP')
#    control_mdp = MDP.control_mdp
#    formulas = MDP.specification_fsm._formulas
#    probs = MDP.specification_fsm._partial_rewards
#    spec_fsm = SpecificationFSM(formulas, probs)
#    MDP = SpecificationMDP(spec_fsm, control_mdp)

    agent = QLearningAgent(MDP)
    print('Training Min regret agent')
    agent.explore(episode_limit = 10000, action_limit = 100000, verbose = True)

    eval_agent = ExplorerAgent(MDP, input_policy=agent.create_learned_softmax_policy(0.01))
    return eval_agent

def active_query(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
#
#    print('Recompiling MDP')
#    control_mdp = MDP.control_mdp
#    formulas = MDP.specification_fsm._formulas
#    probs = MDP.specification_fsm._partial_rewards
#    spec_fsm = SpecificationFSM(formulas, probs)
#    MDP = SpecificationMDP(spec_fsm, control_mdp)

    print('Training an Active query agent')
    query = create_active_query(MDP, verbose = True)
    return query['agent']

def random_query(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
#    print('Recompiling MDP')
#    control_mdp = MDP.control_mdp
#    formulas = MDP.specification_fsm._formulas
#    probs = MDP.specification_fsm._partial_rewards
#    spec_fsm = SpecificationFSM(formulas, probs)
#    MDP = SpecificationMDP(spec_fsm, control_mdp)
    print('Training a Random query agent')
    query = create_random_query(MDP)
    return query['agent']




def process_puns_request(data):
    data = decode_data(data)
    #print(type(data))

    if type(data)==dict:
        if data['request_type'] == 'Puns':
            print('PUnS request received')
            agent = train_puns(data)
        elif data['request_type'] == 'Active':
            print('Active query request received')
            agent = active_query(data)
        elif data['request_type'] == 'Random':
            print('Random query request received')
            agent = random_query(data)
    return agent

def run_puns_server():

    while True:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.bind((HOST,PORT))
            s.listen()

            print('Waiting for Requests \n')
            conn,addr = s.accept()

            with conn:
                print('Receiving data from: ', addr)
                #Get the MDP specification from the client
                raw_data = b''
                while True:
                    newdata = conn.recv(1024*1024)
                    raw_data += newdata
                    if newdata[-4::] == b'DONE': break
                rec_data = raw_data[:-4]

                print('Training agent')
                agent = process_puns_request(rec_data)

                print('\nSending Agent')
                print(agent.__module__)
                conn.sendall(dill.dumps(agent))
                del agent
        print('Request Completed \n\n')



if __name__ == '__main__':

    run_puns_server()

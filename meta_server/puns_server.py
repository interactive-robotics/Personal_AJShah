import socket
import dill
import json
from probability_tools import *
from query_selection import *
from pedagogical_demo import *
from puns.SpecificationFSMTools import SpecificationFSM, CreateReward
from puns.SpecificationMDP import SpecificationMDP
import auto_eval_params as params
import os
import time

HOST = 'localhost'
PORT = 10020

def decode_data(data):
    #try:
    data = dill.loads(data)
    return data

def train_puns(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
    agent = QLearningAgent(MDP)
    print('Training Min regret agent')

    # 220819: Shen: modify the 2nd phase training to 5000.
    # For the final PUnS request, you can change the number of training episodes in the file root/meta_server/puns_server.py, in the train_puns() function, line 26 in the agent.explore() call arguments. We talked about this, and I think 5000 episodes should suffice. 
    # If you want to change the number of episodes for the active query, you will have to change it in Personal_AJShah/meta_server/query_selection.py line 141 in create_active_query() function. For the demo, I think anything less than 5000 and you run the risk of the robot not learning the task correctly. 
    agent.explore(episode_limit = 5000, action_limit = 100000, verbose = True)
    # agent.explore(episode_limit = 10000, action_limit = 100000, verbose = True)

    eval_agent = ExplorerAgent(MDP, input_policy=agent.create_learned_softmax_policy(0.01))
    return eval_agent

def active_query(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
    print('Training an Active query agent')
    query = create_active_query(MDP, verbose = True, query_strategy = data['query_strategy'], k = data['k'])
    return query['agent']

def random_query(data):
    MDP = data['MDP']
    MDP.specification_fsm.reward_function = CreateReward(MDP.specification_fsm._partial_rewards)
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

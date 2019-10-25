#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Created on Thu Oct 24 21:47:23 2019

@author: ajshah
"""

import socket
import dill
import json
from DemoScript import *
import auto_eval_params as params
import os
import time
from puns.utils import CreateSampleMDP, CreateSpecMDP

HOST = 'ajshah.mit.edu'
PORT = 10020
AgentPath = ''

def send_puns_request(data, return_agent = True):
    """Sends the request to the puns server and returns a trained agent to either
    demonstrate a query or to perform the task as per PUnS criterion encoded
    in the MDP request"""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        print('Connected to PUnS Server')

        s.sendall(dill.dumps(data))
        s.sendall(b'DONE')
        req_type = data['request_type']
        print(f'Sent MDP definition for {req_type} request')
        print('\nAwaiting Response ...\n')

        rec_data = b''
        #i=1
        while True:

            newdata = s.recv(1024*1024*10) #Receive 10MB of data at a time
            print(f'\rReceiving Agent policy',end='')
            rec_data += newdata
            i += 1
            if not newdata:
                print('')
                break


        agent_filename = os.path.join(AgentPath, 'Received_Agent.pkl')
        print(f'Agent policy received, saving to {agent_filename}')
        with open(agent_filename, 'wb') as file:
            file.write(rec_data)

        if return_agent:
            return dill.loads(rec_data)


def send_sample_puns_request(request_type = 'Puns'):
    #specification = json.load(open(os.path.join(params.distributions_path, 'batch_posterior.json'),'r'))
    #formulas = specification['support']
    #probs = specifications['probs']
    specfile = os.path.join(params.distributions_path, 'batch_posterior.json')
    MDP = CreateSpecMDP(specfile, 0, 5)
    send_data = {}
    send_data['request_type'] = request_type
    send_data['MDP'] = MDP

    agent = send_puns_request(send_data)
    return agent



if __name__ == '__main__':
    agent = send_sample_puns_request(request_type = 'Active')

import socket
import dill
import json
from DemoScript import *
import auto_eval_params as params
import os
import time

def decode_data(data):
    try:
        data = dill.loads(data)
    except:
        print('data not readable by dill: ', data)
        print('No action taken')
    return data

def process_puns_request(data):
    data = decode_data(data)

    if type(data)==dict:
        if data['request_type'] == 'Puns':
            agent = train_puns(data)
        elif data['request_type'] == 'Active':
            agent = active_query(data)
        elif data['request_type'] == 'Random':
            agent = random_query(data)
    return agent

def run_puns_server():
    
    while True:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.bind((HOST,PORT1))
            s.listen()

            print('Waiting for Requests \n')
            conn,addr = s.accept()

            with conn:
                print('Receiving data from: ', addr)
                #Get the MDP specification from the client
                raw_data = b''
                while True:
                    newdata = conn.recv(4096)
                    raw_data += newdata
                    if newdata[-4::] == b'DONE': break
                rec_data = raw_data[:-4]

                print('Training agent')
                agent = process_puns_request(rec_data)

                print('Sending Agent')
                conn.sendall(dill.dumps(agent))
        print('Request Completed \n\n')



if __name__ == '__main__':
    run_puns_server()
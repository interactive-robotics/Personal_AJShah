import socket
import dill
import json
from DemoScript import *
import auto_eval_params as params
import os
import time

HOST = 'localhost'
PORT1 = 10050
#PORT2 = 10000

def decode_data(data):
    try:
        data = dill.loads(data)
    except:
        print('data not readable by dill: ', data)
        print('No action taken')
    return data

def clear_demonstrations(params):
    files = os.listdir(params.compressed_data_path)
    for f in files:
        os.remove(os.path.join(params.compressed_data_path, f))

def clear_distributions(params):
    files = os.listdir(params.distributions_path)
    for f in files:
        os.remove(os.path.join(params.distributions_path, f))


def batch_bsi(data):

    '''data must be a dict with the keys 'request_type', 'demos'
    data['demos'] is a list of dictionaries each has keys ['trace'] and ['label']
    '''
    #clear existing database
    clear_demonstrations(params)

    #create demonstrations and write the demo files
    for demo in data['demos']:
        new_traj = create_query_demo(demo['trace'])
        write_demo_query_data(new_traj, demo['label'], params.compressed_data_path, filename='demo')

    # Run the inference command
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj 10'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    with open(os.path.join(params.distributions_path,'batch_posterior.json'),'r') as file:
        dist = json.load(file)

    return dist

def active_bsi(data):
    '''data must be a dict with keys  'prior_dist', 'demos',  '''
    #clear existing demonstrations and filenames
    clear_demonstrations(params)
    clear_distributions(params)

    #Write the query to a demo files
    new_traj = create_query_demo(data['demos']['trace'])
    write_demo_query_data(new_traj, data['demos']['label'], params.compressed_data_path,  query_number = 1)

    #Save the prior distributions

    with open(os.path.join(params.distributions_path,'batch_posterior.json'),'w') as file:
        json.dump(data['prior_dist'], file)

    # Run the inference command
    infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery 1'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    with open(os.path.join(params.distributions_path,'batch_posterior.json'),'r') as file:
        dist = json.load(file)

    return dist

def process_request(data):
    data = decode_data(data)
    if type(data) == dict:
        if data['request_type'] == 'Batch':
            print('Batch request received \n')
            dist = batch_bsi(data)
            #print('distribution computed')
        elif data['request_type'] == 'Active':
            print('Active Request Recieved')
            dist = active_bsi(data)
    return dist

def single_socket_server():

    while True:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.bind((HOST,PORT1))
            s.listen()
            print('Waiting for BSI Requests')
            conn,addr = s.accept()

            with conn:
                print('Receiving data from: ', addr)
                raw_data = b''
                while True:
                    newdata = conn.recv(4096)
                    raw_data += newdata
                    #print(newdata[-4::])
                    if newdata[-4::] == b'DONE': break
                rec_data = raw_data[:-4]

                dist = process_request(rec_data)

                print('Distribution Computed')
                print('Sending Data \n')

                conn.sendall(dill.dumps(dist))

        print('Request Completed \n\n')





if __name__ == '__main__':
    #print(dir(params))

    single_socket_server()

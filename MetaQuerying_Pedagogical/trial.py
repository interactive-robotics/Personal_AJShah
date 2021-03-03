from Auto_Eval_Active import *
import os
import sys

def run_single_trial(directory):

    '''directory should include a file 'trial_config.pkl' that acts as arguments'''
    with open(os.path.join(directory,'trial_config.pkl'),'rb') as file:
        data = dill.load(file)

    n_demo = data['n_demo']
    n_query = data['n_query']
    mode = data['mode']
    given_ground_truth = data['given_ground_truth']
    batch_id = data['batch_id']
    command_headers = data['command_headers']
    args = data['args']
    conditions = ['conditions']


    out_data = {}
    out_data['queries_chosen'] = 0
    out_data['demonstrations_chosen'] = 0
    out_data['query_mismatch'] = 0
    out_data['similarity'] = {}
    out_data['entropy'] = {}
    out_data['results'] = {}

    run_id = batch_id
    print(f'Running Trial {run_id}')
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(directory, uncertainty_sampling_params, demo=n_demo, ground_truth_formula = given_ground_truth)

    out_data['results']['ground_truth'] = ground_truth_formula
    for arg in args:
        arg['demo'] = eval_agent
        arg['ground_truth_formula'] = ground_truth_formula
        arg['run_id'] = run_id

    #Save the args in 'Run_Config/run_config.pkl'
    with open(os.path.join(directory, 'run_config.pkl'), 'wb') as file:
        dill.dump({'args': args}, file)

    commands = [f'{c} {directory} {i}' for (i,c) in enumerate(command_headers)']

    with Pool(processes = len(commands)) as pool:
        returnvals = pool.map(os.system, commands)

    for (retval, command) in zip(returnvals, commands):
        if retval:
            retval = os.system(command)

    # Read the respective files from 'Run_Config'
    run_data = []
    files = [f'condition_{i}' for i in range(len(conditions))]
    for file in files:
        with open(os.path.join(directory, file), 'rb') as f:
            data = dill.load(f)
        #os.remove(os.path.join(directory,file))
        run_data.append(data)

    for (c, rd) in zip(command_headers, run_data):

        if 'active' in c:
            out_data['query_mismatch'] = out_data['query_mismatch'] + rd['query_mismatches']
        if 'meta' in c:
            out_data['queries_chosen'] = out_data['queries_chosen'] + rd['queries_performed']
            out_data['demonstrations_chosen'] = out_data['demonstrations_chosen'] = rd['demonstrations_requested']

        out_data['similarity'][condition] = rd['similarity']
        out_data['entropy'][condition] = rd['entropy']
        out_data['results'][condition] = rd['Distributions']

    with open(os.path.join(directory, 'trial_out_data.pkl'), 'wb') as file:
        dill.dump(out_data, file)





if __name__ == '__main__':

    directory = sys.argv[1]
    run_single_trial(directory)

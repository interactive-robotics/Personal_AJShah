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
    conditions = data['conditions']
    p_threats = data['p_threats']
    p_orders = data['p_orders']
    p_waypoints = data['p_waypoints']


    out_data = {}
    out_data['initial_demos'] = {}
    out_data['queries_chosen'] = {}
    out_data['demonstrations_chosen'] = {}
    out_data['query_mismatch_info_gain'] = {}
    out_data['query_mismatch_model_change'] = {}
    out_data['similarity'] = {}
    out_data['entropy'] = {}
    out_data['results'] = {}
    out_data['meta_selections'] = {}
    out_data['query_flags'] = {}
    out_data['labels'] = {}

    run_id = batch_id
    print(f'Running Trial {run_id}')
    demo_directory = os.path.join(directory, 'condition_0', global_params.compressed_data_path)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo_directory, demo=n_demo, ground_truth_formula = given_ground_truth, p_threats = p_threats, p_waypoints = p_waypoints, p_orders = p_orders)

    out_data['results']['ground_truth'] = ground_truth_formula
    for arg in args:
        arg['demo'] = eval_agent
        arg['ground_truth_formula'] = ground_truth_formula
        arg['run_id'] = run_id

    #Save the args in 'Run_Config/run_config.pkl'
    with open(os.path.join(directory, 'run_config.pkl'), 'wb') as file:
        dill.dump({'args': args}, file)

    condition_dirs = [os.path.join(directory, f'condition_{i}') for i in range(len(conditions))]
    print(len(condition_dirs))
    print(len(command_headers))
    commands = [f'{c} {condition_dirs[i]} {i}' for (i,c) in enumerate(command_headers)]

    with Pool(processes = len(commands)) as pool:
        returnvals = pool.map(os.system, commands)

    for (retval, command) in zip(returnvals, commands):
        if retval:
            retval = os.system(command)

    # Read the respective files from 'Run_Config'
    run_data = []
    files = [f'condition_{i}.pkl' for i in range(len(conditions))]
    for file in files:
        with open(os.path.join(directory, file), 'rb') as f:
            data = dill.load(f)
        #os.remove(os.path.join(directory,file))
        run_data.append(data)

    for (c, rd, condition) in zip(command_headers, run_data, conditions):

        if 'active' in c:
            out_data['query_mismatch_info_gain'][condition] = rd['query_mismatches_info_gain']
            out_data['query_mismatch_model_change'][condition] = rd['query_mismatches_model_change']
        if 'meta' in c:
            out_data['queries_chosen'][condition] = rd['queries_performed']
            out_data['demonstrations_chosen'][condition] = rd['demonstrations_requested']
            out_data['meta_selections'][condition] = rd['meta_selections']

        out_data['initial_demos'][condition] = rd['initial_demos']
        out_data['similarity'][condition] = rd['similarity']
        out_data['entropy'][condition] = rd['entropy']
        out_data['results'][condition] = rd['Distributions']
        out_data['query_flags'][condition] = [q['flag'] for q in rd['Queries']]
        out_data['labels'][condition] = [q['label'] for q in rd['Queries']]

    with open(os.path.join(directory, 'trial_out_data.pkl'), 'wb') as file:
        dill.dump(out_data, file)





if __name__ == '__main__':

    directory = sys.argv[1]
    run_single_trial(directory)
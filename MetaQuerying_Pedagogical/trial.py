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


    out_data = {}
    out_data['queries_chosen'] = 0
    out_data['demonstrations_chosen'] = 0
    out_data['query_mismatch'] = 0
    out_data['similarity'] = {}
    out_data['entropy'] = {}
    out_data['results'] = {}

    trial_functions = [run_active_trial, run_active_trial, run_batch_trial, run_meta_selection_trials, run_pedagogical_trials]
    conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Batch', 'Meta-Selection', 'Pedagogical Batch', 'Meta Pedagogical']
    args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
    args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
    args3 = {'n_query': n_query, 'mode': mode}
    args4 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling'}
    args5 = {'n_query': n_query,}
    args4 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'pedagogical': True}
    args = [args1, args2, args3, args4, args5]

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

    commands = [f'python uncertainty_sampling_trial.py {directory}',
                f'python info_gain_trial.py {directory}',
                f'python batch_trial.py {directory}',
                f'python meta_selection_trial.py {directory}',
                f'python pedagogical_trial.py {directory}']
    with Pool(processes = 5) as pool:
        returnvals = pool.map(os.system, commands)

    for (retval, command) in zip(returnvals, commands):
        if retval:
            retval = os.system(command)

    # Read the respective files from 'Run_Config'
    run_data = []
    files = ['uncertainty_sampling.pkl','info_gain.pkl','batch.pkl','meta_selection.pkl', 'pedagogical.pkl']
    for file in files:
        with open(os.path.join(directory, file), 'rb') as f:
            data = dill.load(f)
        #os.remove(os.path.join(directory,file))
        run_data.append(data)

    for (condition, rd) in zip(conditions, run_data):

        if condition == 'Active: Uncertainty Sampling' or condition == 'Active: Info Gain':
            out_data['query_mismatch'] = out_data['query_mismatch'] + rd['query_mismatches']
        if condition == 'Meta-Selection':
            out_data['queries_chosen'] = out_data['queries_chosen'] + rd['queries_performed']
            out_data['demonstrations_chosen'] = out_data['demonstrations_chosen'] = rd['demonstrations_requested']

        out_data['similarity'][condition] = rd['similarity']
        out_data['entropy'][condition] = rd['entropy']
        out_data['results'][condition] = rd['Distributions'][-1]

    with open(os.path.join(directory, 'trial_out_data.pkl'), 'wb') as file:
        dill.dump(out_data, file)





if __name__ == '__main__':

    directory = sys.argv[1]
    run_single_trial(directory)

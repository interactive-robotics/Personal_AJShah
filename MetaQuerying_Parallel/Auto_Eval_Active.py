from query_selection import *
from utils import *
from formula_utils import *
from puns.utils import CreateSpecMDP, Eventually, Order, Globally
from puns.SpecificationMDP import *
from puns.LearningAgents import QLearningAgent
from puns.Exploration import ExplorerAgent
from numpy.random import binomial
import numpy as np
from scipy.stats import entropy
from matplotlib.backends.backend_pdf import PdfPages
import dill
import params.auto_eval_params as global_params
import params.uncertainty_sampling_params as uncertainty_sampling_params
import params.info_gain_params as info_gain_params
import params.batch_params as batch_params
import params.meta_params as meta_params
import os
import json
from copy import deepcopy
from multiprocessing import Pool
from itertools import repeat


def apply(f,x):
    return f(**x)

def run_parallel_trials(trials = 200, n_demo = 2, n_query = 4, given_ground_truth_formula = None, mode = 'incremental'):
    summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
    if os.path.exists(summary_file):
        with open(summary_file,'rb') as file:
            out_data = dill.load(file)
            start_id = len(out_data['similarity'].keys())
    else:
        out_data = {}
        start_id = 0
        out_data['queries_chosen'] = 0
        out_data['demonstrations_chosen'] = 0
        out_data['query_mismatch'] = 0
        out_data['similarity'] = {}
        out_data['entropy'] = {}
        out_data['results'] = {}

    #Metrics to collect for each run: Similarity, Entropy, ground_truth formula, distribution
    #Global metrics: number of queries chosen, number of demonstrations chosen, query_mismatches
    trial_functions = [run_active_trial, run_active_trial, run_batch_trial, run_meta_selection_trials]
    conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Batch', 'Meta-Selection']
    args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
    args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
    args3 = {'n_query': n_query, 'mode': mode}
    args4 = {'n_query': n_query, 'query_strategy': 'info_gain'}
    args = [args1, args2, args3, args4]

    for i in range(n_trials):

            run_id = start_id + i
            print(f'Running Trial {run_id}')
            n_demo, eval_agent, ground_truth_formula = ground_truth_selector(uncertainty_sampling_params, demo=n_demo, ground_truth_formula = given_ground_truth_formula)

        out_data['similarity'][run_id] = {}
        out_data['entropy'][run_id] = {}
        out_data['results'][run_id] = {}
        out_data['results'][run_id]['ground_truth'] = ground_truth_formula

        for arg in args:
            arg['demo'] = eval_agent
            arg['ground_truth_formula'] = ground_truth_formula
            arg['run_id'] = run_id

        #Save the args in 'Run_Config/run_config.pkl'
        with open('Run_Config/run_config.pkl', 'wb') as file:
            dill.dump({'args': args}, file)

        commands = ['python uncertainty_sampling_trial.py',
                    'python info_gain_trial.py',
                    'python batch_trial.py',
                    'python meta_selection_trial.py']


        with Pool(processes = 4) as pool:
            returnvals = pool.map(os.system, commands)

        for (retval, command) in zip(returnvals, commands):
            if retval:
                retval = os.system(command)

        # Read the respective files from 'Run_Config'
        run_data = []
        files = ['uncertainty_sampling.pkl','info_gain.pkl','batch.pkl','meta_selection.pkl']
        for file in files:
            with open(os.path.join('Run_Config', file), 'rb') as f:
                data = dill.load(f)
            os.remove(os.path.join('Run_Config',file))
            run_data.append(data)


        for (condition, rd) in zip(conditions, run_data):

            if condition == 'Active: Uncertainty Sampling' or condition == 'Active: Info Gain':
                out_data['query_mismatch'] = out_data['query_mismatch'] + rd['query_mismatches']
            if condition == 'Meta-Selection':
                out_data['queries_chosen'] = out_data['queries_chosen'] + rd['queries_performed']
                out_data['demonstrations_chosen'] = out_data['demonstrations_chosen'] = rd['demonstrations_requested']

            out_data['similarity'][run_id][condition] = rd['similarity']
            out_data['entropy'][run_id][condition] = rd['entropy']
            out_data['results'][run_id][condition] = rd['Distributions'][-1]

        summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
        with open(summary_file,'wb') as file:
            dill.dump(out_data,file)



    #Write to file in results path and return
    return out_data


def run_paired_trials(trials = 200, n_demo = 2, n_query = 4, ground_truth_formula = None, mode = 'incremental'):

    #Making this incremental
    #Check if the results path already exists
    summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
    if os.path.exists(summary_file):
        with open(summary_file,'rb') as file:
            out_data = dill.load(file)
            start_id = len(out_data['similarity'].keys())
    else:
        out_data = {}
        start_id = 0
        out_data['queries_chosen'] = 0
        out_data['demonstrations_chosen'] = 0
        out_data['query_mismatch'] = 0
        out_data['similarity'] = {}
        out_data['entropy'] = {}
        out_data['results'] = {}


    #Metrics to collect for each run: Similarity, Entropy, ground_truth formula, distribution

    #Global metrics: number of queries chosen, number of demonstrations chosen, query_mismatches


    trial_functions = [run_active_trial, run_active_trial, run_batch_trial, run_meta_selection_trials]
    conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Batch', 'Meta-Selection']
    args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
    args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
    args3 = {'n_query': n_query, 'mode': mode}
    args4 = {'n_query': n_query, 'query_strategy': 'info_gain'}
    args = [args1, args2, args3, args4]

    for i in range(trials):

        run_id = start_id + i
        n_demo, eval_agent, ground_truth_formula = ground_truth_selector(uncertainty_sampling_params, demo=n_demo, ground_truth_formula = ground_truth_formula)
        #Initialize the run information

        out_data['similarity'][run_id] = {}
        out_data['entropy'][run_id] = {}
        out_data['results'][run_id] = {}
        out_data['results'][run_id]['ground_truth'] = ground_truth_formula

        for (trial_func, condition, kwarg) in zip(trial_functions, conditions, args):
            #Initialize the dictionary for this run


            #set the ground_truth conditions and initial demonstrations
            kwarg['demo'] = eval_agent
            kwarg['ground_truth_formula'] = ground_truth_formula
            kwarg['run_id'] = run_id

            run_data = trial_func(**kwarg)

            #add query mismatch information for the active trials
            if trial_func == run_active_trial:
                out_data['query_mismatch'] = out_data['query_mismatch'] + run_data['query_mismatches']
            if trial_func == run_meta_selection_trials:
                out_data['queries_chosen'] = out_data['queries_chosen'] + run_data['queries_performed']
                out_data['demonstrations_chosen'] = out_data['demonstrations_chosen'] + run_data['demonstrations_requested']

            out_data['similarity'][run_id][condition] = run_data['similarity']
            out_data['entropy'][run_id][condition] = run_data['entropy']
            out_data['results'][run_id][condition] = run_data['Distributions'][-1]

    # out_data['similarity'] = pd.DataFrame.from_dict(out_data['similarity'], orient='index')
    # out_data['entropy'] = pd.DataFrame.from_dict(out_data['entropy'], orient='index')
    # out_data['similarity'] = pd.DataFrame.from_dict(out_data['similarity'], orient='index')
        #Summary file should be written at the end of every trial
        summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
        with open(summary_file,'wb') as file:
            dill.dump(out_data,file)



    #Write to file in results path and return
    return out_data

def run_meta_selection_trials(demo = 2, n_query = 4, query_strategy = 'info_gain',
run_id = 1, ground_truth_formula = None, write_file = True, verbose=True):

    params = meta_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0
    queries_performed = 0
    demonstrations_requested = 0

    clear_demonstrations(params)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(params, demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1]))

    for i in range(n_query):

        #Determine if additional demonstration or query will yield larger entropy gain
        state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type = 'info_gain')
        query_gain = compute_expected_entropy_gain(state, MDPs[-1].specification_fsm)
        print('Query Gain:', query_gain)
        demonstration_gain = compute_expected_entropy_gain_demonstrations(MDPs[-1].specification_fsm)
        print('Demonstration Gain:', demonstration_gain)
        demo = True if demonstration_gain >= query_gain else False

        if demo:
            if verbose: print('Selecting demonstration for next data point')
            demonstrations_requested = demonstrations_requested + 1

            #create a demonstration as a positive query
            eval_agent.explore(1)
            MDP = eval_agent.MDP
            record = eval_agent.episodic_record[-1]
            trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
            trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))
            new_traj = create_query_demo(trace_slices)
            write_demo_query_data(new_traj, True, params.compressed_data_path, query_number=i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after demo {n_demo+i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
            Distributions.append(extract_dist(MDPs[-1]))
        else:
            #learn from an active info gain query
            if verbose: print(f'Trial {run_id}: Selecting Query for next data point')
            queries_performed = queries_performed + 1

            #Create the query
            if verbose: print(f'Trial {run_id}: Generating query {i+1} demo')
            Queries.append(create_active_query(MDPs[-1], verbose=verbose, non_terminal = global_params.non_terminal, query_strategy = query_strategy))
            Queries[-1]['agent'] = 1

            #Elicit label feedback from the ground truth
            signal = create_signal(Queries[-1]['trace'])
            label = Progress(ground_truth_formula, signal)[0]
            if verbose:
                print(f'Trial {run_id}: Generating ground truth label for query {i+1}')
                print('Assigned label', label)

            # Writing the query data to the inference database
            new_traj = create_query_demo(Queries[-1]['trace'])
            write_demo_query_data(new_traj, label, params.compressed_data_path, query_number = i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after query {i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
            Distributions.append(extract_dist(MDPs[-1]))

    similarities = [compare_distribution(ground_truth_formula, dist) for dist in Distributions]
    out_data = {}
    out_data['similarities'] = similarities
    out_data['similarity'] = similarities[-1]
    out_data['entropy'] = entropy(Distributions[-1]['probs'])
    out_data['Distributions'] = Distributions
    out_data['MDPs'] = MDPs
    out_data['Queries'] = Queries
    out_data['ground_truth_formula'] = ground_truth_formula
    out_data['run_id'] = run_id
    out_data['type'] = query_strategy
    out_data['query_mismatches'] = query_mismatches
    out_data['demonstrations_requested'] = demonstrations_requested
    out_data['queries_performed'] = queries_performed

    if write_file:
        write_run_data_new(out_data, run_id, typ = f'Meta_Selection')
        create_run_log(run_id, f'Meta_Selection')
    return out_data

def run_batch_trial(demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None, mode = 'incremental', write_file = True, verbose=True):
    params = batch_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0

    clear_demonstrations(params)

    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(params, demo, ground_truth_formula)

    if mode == 'incremental':


        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
        Distributions.append(extract_dist(MDPs[-1]))

        #Add each demonstration one after the other
        for i in range(n_query):



            #create a demonstration as a positive query
            eval_agent.explore(1)
            MDP = eval_agent.MDP
            record = eval_agent.episodic_record[-1]
            trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
            trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))
            new_traj = create_query_demo(trace_slices)
            write_demo_query_data(new_traj, True, params.compressed_data_path, query_number=i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after demo {n_demo+i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
            Distributions.append(extract_dist(MDPs[-1]))

    else:
        mode = 'batch'
        #create all demonstrations and run inference only once
        eval_agent.explore(n_query)
        MDP = eval_agent.MDP
        for record in eval_agent.episodic_record[-n_query::]:
            trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
            trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))
            new_traj = create_query_demo(trace_slices)
            write_demo_query_data(new_traj, True, params.compressed_data_path, filename = 'Demo')

        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
        Distributions.append(extract_dist(MDPs[-1]))

    similarities = [compare_distribution(ground_truth_formula, dist) for dist in Distributions]
    out_data = {}
    out_data['similarities'] = similarities
    out_data['similarity'] = similarities[-1]
    out_data['entropy'] = entropy(Distributions[-1]['probs'])
    out_data['Distributions'] = Distributions
    out_data['MDPs'] = MDPs
    out_data['Queries'] = Queries
    out_data['ground_truth_formula'] = ground_truth_formula
    out_data['run_id'] = run_id
    out_data['type'] = 'Demo'
    out_data['query_mismatches'] = query_mismatches

    if write_file:
        write_run_data_new(out_data, run_id, typ = f'Demo')
        create_run_log(run_id, 'Demo')
    return out_data

def run_active_trial(query_strategy = 'uncertainty_sampling', demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None,
verbose = True, write_file = True):

    if query_strategy == 'uncertainty_sampling':
        params = uncertainty_sampling_params
    else:
        params = info_gain_params

    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0

    clear_demonstrations(params)

    print(f'Trial {run_id}: Running Active trial {query_strategy}')

    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(params, demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1],))

    #For the number of budgeted Queries
    for i in range(n_query):

        #Check for mismatch between info gain and uncertainty Sampling
        uncertainty_sampling_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type = 'uncertainty_sampling')
        infogain_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type='info_gain')
        if uncertainty_sampling_desired_state != infogain_desired_state: query_mismatches = query_mismatches + 1

        #Create the query
        if verbose: print(f'Trial {run_id}: Generating query {i+1} demo')
        Queries.append(create_active_query(MDPs[-1], verbose=verbose, non_terminal = global_params.non_terminal, query_strategy = query_strategy))
        Queries[-1]['agent'] = 1

        #Elicit label feedback from the ground truth
        signal = create_signal(Queries[-1]['trace'])
        label = Progress(ground_truth_formula, signal)[0]
        if verbose:
            print(f'Trial {run_id}: Generating ground truth label for query {i+1}')
            print('Assigned label', label)

        # Writing the query data to the inference database
        new_traj = create_query_demo(Queries[-1]['trace'])
        write_demo_query_data(new_traj, label, params.compressed_data_path, query_number = i+1)

        # Update the posterior distribution using active BSI
        if verbose: print(f'Trial {run_id}: Updating posterior after query {i+1}')
        infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference failure')

        # Recompile the MDP with the updated specification and add the distributions
        spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
        Distributions.append(extract_dist(MDPs[-1]))

    last_dist = Distributions[-1]
    similarities = [compare_distribution(ground_truth_formula, dist) for dist in Distributions]

    out_data = {}
    out_data['similarities'] = similarities
    out_data['similarity'] = similarities[-1]
    out_data['Distributions'] = Distributions
    out_data['entropy'] = entropy(Distributions[-1]['probs'])
    out_data['MDPs'] = MDPs
    out_data['Queries'] = Queries
    out_data['ground_truth_formula'] = ground_truth_formula
    out_data['run_id'] = run_id
    out_data['type'] = f'Active_{query_strategy}'
    out_data['query_mismatches'] = query_mismatches



    if write_file:
        write_run_data_new(out_data, run_id, typ = f'Active_{query_strategy}')
        create_run_log(run_id, f'Active_{query_strategy}')
    return out_data


def write_run_data_new(out_data, run_id, typ):
    if not os.path.exists(os.path.join(global_params.results_path,'Runs')): os.mkdir(os.path.join(global_params.results_path,'Runs'))
    filename = os.path.join(global_params.results_path, 'Runs', f'{typ}_Run_{run_id}.pkl')
    out_data['Queries'] = [q['trace'] for q in out_data['Queries']]
    with open(filename, 'wb') as file:
        dill.dump(out_data, file)



def ground_truth_selector(params, demo = 2, ground_truth_formula = None):
    if ground_truth_formula == None:
        ground_truth_formula = sample_ground_truth()

    if type(demo) == int:
        n_demo = demo
        eval_agent = create_demonstrations(ground_truth_formula, n_demo, params)
    else:
        n_demo = len(demo.episodic_record)
        record_agent_episodes(demo, params)
        eval_agent = deepcopy(demo)
    return n_demo, eval_agent, ground_truth_formula

def record_agent_episodes(eval_agent, params):
    MDP = eval_agent.MDP
    for record in eval_agent.episodic_record:

        trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
        trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

        new_traj = create_query_demo(trace_slices)

        write_demo_query_data(new_traj, True, params.compressed_data_path, filename='demo')

def write_run_data(Distributions, MDPs, Queries, ground_truth_formula, run_id, type = 'Active'):
    if not os.path.exists(os.path.join(global_params.results_path,'Runs')): os.mkdir(os.path.join(global_params.results_path,'Runs'))
    filename = os.path.join(global_params.results_path, 'Runs', f'{type}_Run_{run_id}.pkl')
    data = {}
    data['Distributions'] = Distributions
    data['MDPs'] = MDPs
    data['Queries'] = [q['trace'] for q in Queries]
    data['True_Formula'] = ground_truth_formula

    with open(filename,'wb') as file:
        dill.dump(data, file)

def create_run_log(run_id, type = 'Active'):
    filename = os.path.join(global_params.results_path, 'Runs', f'{type}_Run_{run_id}')
    with open(filename+'.pkl','rb') as file:
        data = dill.load(file)

    if type == 'Demo':
        n_demo = global_params.n_demo + global_params.n_queries
    else:
        n_demo = global_params.n_demo

    pdf_file = filename+'.pdf'
    with PdfPages(pdf_file) as pdf:
        #print the ground truth formula
        plt.figure()
        true_form = json.dumps(data['ground_truth_formula'])
        plt.text(0,0,true_form, wrap = True)
        plt.axis([-0.1,1,-1,1])
        plt.title(f'Trial {run_id}: Ground truth')
        pdf.savefig()
        plt.close()

        # Plot the original batch distributions
        plt.figure(figsize = (5,5))
        probs = data['Distributions'][0]['probs']
        plt.bar(list(range(len(probs))), probs)
        plt.title(f'Trial {run_id}: Posterior after {n_demo} demonstrations')
        pdf.savefig()
        plt.close()

        for i in range(len(data['Queries'])):
            #plot the query_
            plt.figure(figsize=(5,5))
            visualize_query(data['Queries'][i])
            plt.title(f'Query {i+1}')
            pdf.savefig()
            plt.close()

            #plot the distribution after the query_
            plt.figure(figsize = (5,5))
            probs = data['Distributions'][i+1]['probs']
            plt.bar(list(range(len(probs))), probs)
            plt.title(f'Posterior after query {i+1}')
            pdf.savefig()
            plt.close()

        # Print the MAP
        plt.figure()
        true_form = json.dumps(data['Distributions'][-1]['formulas'][0])
        plt.text(0,0,true_form, wrap=True)
        entropyval = entropy(data['Distributions'][-1]['probs'])
        plt.text(0, -0.9, f'Entropy: {entropyval}')
        plt.axis([-0.1,1,-1,1])
        plt.title(f'Trial {run_id}: MAP')
        pdf.savefig()
        plt.close()





def extract_dist(MDP:SpecificationMDP):
    new_dist = {}
    new_dist['formulas'] = MDP.specification_fsm._all_formulas
    new_dist['probs'] = MDP.specification_fsm._all_probs
    return new_dist

def create_demonstrations(formula, nDemo, params, verbose = True, n_threats = 0):

    specification_fsm = SpecificationFSM(formulas=[formula], probs = [1])
    control_mdp = SyntheticMDP(0,global_params.n_waypoints)
    MDP = SpecificationMDP(specification_fsm, control_mdp)

    q_agent = QLearningAgent(MDP)
    print('Training ground truth demonstrator')
    q_agent.explore(episode_limit = 5000, verbose=verbose, action_limit = 1000000)
    eval_agent = ExplorerAgent(MDP, input_policy=q_agent.create_learned_softmax_policy(0.005))
    print('\n')
    eval_agent.explore(episode_limit = nDemo)

    for record in eval_agent.episodic_record:

        trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
        trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

        new_traj = create_query_demo(trace_slices)

        write_demo_query_data(new_traj, True, params.compressed_data_path, filename='demo')
    return eval_agent


def create_results_path():
    if not os.path.exists(global_params.results_path):
        os.mkdir(global_params.results_path)
        os.mkdir(os.path.join(global_params.results_path, 'Runs'))

'''DEPRECATED CODE'''
def run_active_query_trial(query_strategy = 'uncertainty_sampling', n_demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None, verbose=True, write_file=True):

    '''NOW DEPRECATED'''
    MDPs = [] #The list of all the MDPs compiled

    Distributions = []
    '''The list of the distributions computed inferred
    Each entry is a dictionary with keys 'formulas' and 'probs'
    can be used to compute the entropies
    '''
    Queries = []
    '''The list of the queries generated by the active query mechanism
    Each entry is a dictionary with keys 'trace', 'agent' and 'desired state'
    '''
    #Clear the data from previous runs
    clear_demonstrations(params)

    #Start running the queries and active Inference
    for i in range(n_query):

        # Create the query
        if verbose: print(f'Trial {run_id}: Generating query {i+1} demo')
        Queries.append(create_active_query(MDPs[-1], verbose=verbose, non_terminal = params.non_terminal))

        # Eliciting feedback label for the query from ground ground_truth_formula
        signal = create_signal(Queries[-1]['trace'])
        label = Progress(ground_truth_formula, signal)[0]
        if verbose:
            print(f'Trial {run_id}: Generating ground truth label for query {i+1}')
            print('Assigned label', label)

        # Writing the query data to the inference database
        new_traj = create_query_demo(Queries[-1]['trace'])
        write_demo_query_data(new_traj, label, params.compressed_data_path, query_number = i+1)

        # Update the posterior distribution using active BSI
        if verbose: print(f'Trial {run_id}: Updating posterior after query {i+1}')
        infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference failure')

        # Recompile the MDP with the updated specification and add the distributions
        spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
        Distributions.append(extract_dist(MDPs[-1]))

    if write_file:
        write_run_data(Distributions, MDPs, Queries, ground_truth_formula, run_id, type='Active')
    return Distributions, MDPs, Queries, ground_truth_formula

def check_results_path(results_path):
    if not os.path.exists(results_path):
       os.mkdir(results_path)
       os.mkdir(os.path.join(results_path, 'Runs'))

if __name__ == '__main__':


    '''MAIN SCRIPT: Running Paired Trials'''
    global_params.results_path = '/home/ajshah/Results/Test_Meta'
    check_results_path(global_params.results_path)

    n_trials = 175
    n_demo = 2
    n_query = [4]

    for n_q in n_query:
        n_data = n_demo + n_q
        global_params.results_path = f'/home/ajshah/Results/Results_{n_data}_meta'
        check_results_path(global_params.results_path)
        results = run_parallel_trials(trials = n_trials, n_demo = n_demo, n_query = n_q)


    n_trials = 33
    n_demo = 2
    n_query = [2]

    for n_q in n_query:
        n_data = n_demo + n_q
        global_params.results_path = f'/home/ajshah/Results/Results_{n_data}_meta'
        check_results_path(global_params.results_path)
        results = run_parallel_trials(trials = n_trials, n_demo = n_demo, n_query = n_q)



    n_trials = 200
    n_demo = 2
    n_query = [1,5]

    for n_q in n_query:
        n_data = n_demo + n_q
        global_params.results_path = f'/home/ajshah/Results/Results_{n_data}_meta'
        check_results_path(global_params.results_path)
        results = run_paired_trials(trials = n_trials, n_demo = n_demo, n_query = n_q)
    results = run_parallel_trials(trials = n_trials, n_demo = n_demo, n_query = n_q)


#
#    '''Test vanilla active learning in uncertainty sampling mode'''
#    out_data = run_active_trial(query_strategy = 'uncertainty_sampling')
#
#
#    '''Test vanilla active learning in uncertainty sampling mode'''
#    out_data = run_active_trial(query_strategy = 'uncertainty_sampling')
#
    # '''Test uncertainty sampling mode with predefined demonstrations'''
    # ground_truth_formula = sample_ground_truth(5)
    # eval_agent = create_demonstrations(ground_truth_formula, 2)
    #
    # Distributions, MDPs, Queries, ground_truth_formula, query_mismatches = run_active_trial(query_strategy = 'uncertainty_sampling', demo = eval_agent, ground_truth_formula = ground_truth_formula)
    #
    # '''Run batch trial in batch mode'''
    # out_data = run_batch_trial(demo = eval_agent, mode = 'batch', ground_truth_formula = ground_truth_formula)
    #
    # '''Run batch trial in incremental mode'''
    # out_data = run_batch_trial(demo = eval_agent, mode = 'incremental', ground_truth_formula = ground_truth_formula)

    #out_data = run_meta_selection_trials()

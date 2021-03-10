from probability_tools import *
from query_selection import *
from utils import *
from pedagogical_demo import *
import trial_config

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
import params.pedagogical_params as pedagogical_params
import params.meta_pedagogical_params as meta_pedagogical_params
import os
import json
from copy import deepcopy
from multiprocessing import Pool
from itertools import repeat
import re


def apply(f,x):
    return f(**x)

def strip(string):
    return re.sub('[^A-Za-z0-9 ]+', '', string)

def run_parallel_trials(args, command_headers, conditions, batches = 100, workers = 2, n_demo = 2, n_query = 4,
given_ground_truth = None, p_threats = 0.5, p_waypoints=0.5, p_orders = 0.5, mode = 'incremental', query_strategy = 'uncertainty_sampling'):

    summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
    if os.path.exists(summary_file):
        with open(summary_file,'rb') as file:
            out_data = dill.load(file)
            start_id = len(out_data['similarity'].keys())
    else:
        out_data = {}
        start_id = 0
        out_data['queries_chosen'] = {}
        out_data['demonstrations_chosen'] = {}
        out_data['query_mismatch_info_gain'] = {}
        out_data['query_mismatch_model_change'] = {}
        out_data['similarity'] = {}
        out_data['entropy'] = {}
        out_data['results'] = {}

    #Create the trial directories
    for i in range(workers):
        create_trial_directory('Run_Config', i, conditions)

    directories = [os.path.join('Run_Config', f'trial_{i}') for i in range(workers)]

    #Create the trial_config
    trial_config = {
                    'n_demo': n_demo,
                    'n_query': n_query,
                    'given_ground_truth': given_ground_truth,
                    'mode': mode,
                    'args': args,
                    'command_headers': command_headers,
                    'conditions': conditions,
                    'p_threats': p_threats,
                    'p_waypoints': p_waypoints,
                    'p_orders': p_orders
                    }

    for batch_id in range(batches):

        #Write the trial directories
        for (k,directory) in enumerate(directories):
            trial_config['batch_id'] = start_id + workers*batch_id + k
            with open(os.path.join(directory, 'trial_config.pkl'),'wb') as file:
                dill.dump(trial_config, file)

        trial_commands = [f'python trial.py {directory}' for directory in directories]
        with Pool(processes = workers) as pool:
            returnvals = pool.map(os.system, trial_commands)

        #If any run did not succeed, run it in series
        for (retval, command) in zip(returnvals, trial_commands):
            if retval:
                retval = os.system(command)

        for (k,directory) in enumerate(directories):
            #Record all individual runs
            run_id = start_id + workers*batch_id + k
            run_data = []
            files = [f'condition_{i}.pkl' for i in range(len(conditions))]

            #files = ['uncertainty_sampling.pkl','info_gain.pkl','batch.pkl','meta_selection.pkl', 'pedagogical.pkl', 'meta_pedagogical.pkl']
            #typs = ['Active_uncertainty_sampling', 'Active_info_gain', 'Batch', 'Meta_Selection', 'Pedagogical_Batch', 'Meta_Pedagogical']
            typs = [strip(x).replace(' ', '_') for x in conditions]
            for (file, typ) in zip(files, typs):
                with open(os.path.join(directory, file), 'rb') as f:
                    data = dill.load(f)
                write_run_data_new(data, run_id, typ = typ)
                create_run_log(run_id, typ)
                os.remove(os.path.join(directory,file))
                run_data.append(data)

            #Assimilate trial data into the final out_data
            with open(os.path.join(directory, 'trial_out_data.pkl'),'rb') as file:
                trial_out_data = dill.load(file)

            out_data['similarity'][run_id] = trial_out_data['similarity']
            out_data['entropy'][run_id] = trial_out_data['entropy']
            out_data['results'][run_id] = trial_out_data['results']
            out_data['query_mismatch_info_gain'][run_id] = trial_out_data['query_mismatch_info_gain']
            out_data['query_mismatch_model_change'][run_id] = trial_out_data['query_mismatch_model_change']
            out_data['demonstrations_chosen']['run_id'] = trial_out_data['demonstrations_chosen']
            out_data['queries_chosen'][run_id] = trial_out_data['queries_chosen']
            out_data['meta_selections'][run_id] = trial_out_data['meta_selections']

            summary_file = os.path.join(global_params.results_path,'paired_summary.pkl')
            with open(summary_file,'wb') as file:
                dill.dump(out_data,file)

    return out_data


def run_pedagogical_trials(directory, demo = 2, n_query = 4, selectivity = None, query_strategy = 'info_gain',
run_id = 1, ground_truth_formula = None, write_file = False, verbose=True):

    params = global_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = []
    queries_performed = []
    demonstrations_requested = []

    clear_demonstrations(directory, params)
    demo_directory = os.path.join(directory, params.compressed_data_path)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo_directory, demo, ground_truth_formula)

    # Run Batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1]))

    for i in range(n_query):
        demo = create_pedagogical_demo(ground_truth_formula, MDPs[-1], selectivity)
        label = True
        demo['label'] = True

        new_traj = create_query_demo(demo['trace'])
        write_demo_query_data(new_traj, label, os.path.join(directory, params.compressed_data_path), query_number = i+1)
        demo['agent'] = 1
        demo['type'] = 'Demonstration'
        Queries.append(demo)

        # Update the posterior distribution using active BSI
        if verbose: print(f'Trial {run_id}: Updating posterior after demo {n_demo+i+1}')
        infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nQuery {i+1}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference failure')

        # Recompile the MDP with the updated specification and add the distributions
        spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
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
        write_run_data_new(out_data, run_id, typ = f'Pedagogical_Batch')
        create_run_log(run_id, f'Pedagogical_Batch')
    return out_data



def run_meta_selection_trials(directory, demo = 2, n_query = 4, meta_policy = 'info_gain,', query_strategy = 'uncertainty_sampling',
run_id = 1, ground_truth_formula = None, pedagogical=False, selectivity = None, write_file = False, verbose=True):

    params = global_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0
    queries_performed = 0
    demonstrations_requested = 0
    meta_selections = []

    clear_demonstrations(directory, params)
    demo_directory = os.path.join(directory, params.compressed_data_path)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo_directory, demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1]))

    for i in range(n_query):

        #Determine if additional demonstration or query will yield larger entropy gain
        demo, demonstration_gain, query_gain = run_meta_policy(MDPs[-1].specification_fsm, meta_policy, query_strategy, pedagogical, selectivity)
        print('Query Gain:', query_gain)
        print('Demonstration Gain:', demonstration_gain)

        if demo:
            meta_selections.append('demo')
            if verbose: print('Selecting demonstration for next data point')
            demonstrations_requested = demonstrations_requested + 1

            if pedagogical:
                demo = create_pedagogical_demo(ground_truth_formula, MDPs[-1], selectivity)
                trace_slices = demo['trace']
            else:
            #create a demonstration as a positive query
                eval_agent.explore(1)
                MDP = eval_agent.MDP
                record = eval_agent.episodic_record[-1]
                trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
                trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

            new_traj = create_query_demo(trace_slices)
            write_demo_query_data(new_traj, True, os.path.join(directory, params.compressed_data_path), query_number=i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after demo {n_demo+i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            new_query = {}
            new_query['trace'] = trace_slices
            new_query['agent'] = 1
            new_query['label'] = True
            new_query['type'] = 'Demonstration'
            Queries.append(new_query)

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
            Distributions.append(extract_dist(MDPs[-1]))
        else:
            meta_selections.append('query')
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
            write_demo_query_data(new_traj, label, os.path.join(directory, params.compressed_data_path), query_number = i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after query {i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            Queries[-1]['type'] = 'Query'
            Queries[-1]['label'] = label

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
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
    out_data['meta_selections'] = meta_selections

    if write_file:
        if pedagogical:
            write_run_data_new(out_data, run_id, typ = f'Meta_Pedagogical')
            create_run_log(run_id, f'Meta_Pedagogical')
        else:
            write_run_data_new(out_data, run_id, typ = f'Meta_Selection')
            create_run_log(run_id, f'Meta_Selection')
    return out_data

def run_batch_trial(directory, demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None, mode = 'incremental', write_file = False, verbose=True):
    params = global_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0

    clear_demonstrations(directory, params)

    demo_directory = os.path.join(directory, params.compressed_data_path)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo_directory, demo, ground_truth_formula)

    if mode == 'incremental':


        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
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
            write_demo_query_data(new_traj, True, os.path.join(directory, params.compressed_data_path), query_number=i+1)

            # Update the posterior distribution using active BSI
            if verbose: print(f'Trial {run_id}: Updating posterior after demo {n_demo+i+1}')
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            new_query = {}
            new_query['trace'] = trace_slices
            new_query['label'] = True
            new_query['agent'] = 1
            new_query['type'] = 'Demonstration'
            Queries.append(new_query)

            # Recompile the MDP with the updated specification and add the distributions
            spec_file  = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
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
            write_demo_query_data(new_traj, True, os.path.join(directory, params.compressed_data_path), filename = 'Demo')

        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(directory, params.distributions_path, 'batch_posterior.json')
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

def run_active_trial(directory, query_strategy = 'uncertainty_sampling', demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None,
verbose = True, write_file = False):

    params = global_params
    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches_info_gain = 0
    query_mismatches_model_change = 0

    clear_demonstrations(directory, params)

    print(f'Trial {run_id}: Running Active trial {query_strategy}')\

    demo_directory = os.path.join(directory, params.compressed_data_path)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo_directory, demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory, params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(os.path.join(directory, params.distributions_path), 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = global_params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1],))

    #For the number of budgeted Queries
    for i in range(n_query):

        #Check for mismatch between info gain and uncertainty Sampling
        uncertainty_sampling_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type = 'uncertainty_sampling')
        infogain_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type='info_gain')
        max_model_change_desired_state,_ = identify_desired_state(MDPs[-1].specification_fsm, query_type = 'max_model_change')
        if uncertainty_sampling_desired_state != infogain_desired_state: query_mismatches_info_gain = query_mismatches_model_change + 1
        if uncertainty_sampling_desired_state != max_model_change_desired_state: query_mismatches_model_change = query_mismatches_model_change + 1

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
        write_demo_query_data(new_traj, label, os.path.join(directory, params.compressed_data_path), query_number = i+1)

        # Update the posterior distribution using active BSI
        if verbose: print(f'Trial {run_id}: Updating posterior after query {i+1}')
        infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {global_params.n_samples}  --nBurn {global_params.n_burn} --dataPath \'{os.path.join(directory,params.compressed_data_path)}\' --outPath \'{os.path.join(directory, params.distributions_path)}\' --nQuery {i+1}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference failure')

        Queries[-1]['type'] = 'Query'
        Queries[-1]['label'] = label

        # Recompile the MDP with the updated specification and add the distributions
        spec_file = spec_file = os.path.join(os.path.join(directory, params.distributions_path), 'batch_posterior.json')
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
    out_data['query_mismatches_info_gain'] = query_mismatches_info_gain
    out_data['query_mismatches_model_change'] = query_mismatches_model_change



    if write_file:
        write_run_data_new(out_data, run_id, typ = f'Active_{query_strategy}')
        create_run_log(run_id, f'Active_{query_strategy}')
    return out_data

def run_meta_policy(spec_fsm:SpecificationFSM, meta_policy = 'information_gain', query_type = 'uncertainty_sampling', pedagogical = True, selectivity = None):
    query_state,_ = identify_desired_state(spec_fsm, query_type = query_type)
    if meta_policy == 'info_gain':
        query_gain = compute_expected_entropy_gain(query_state, spec_fsm)
        demonstration_gain = compute_expected_entropy_gain_demonstrations(spec_fsm, pedagogical, selectivity)
        #demo = True if demonstration_entropy_gain >= query_entropy_gain
    elif meta_policy == 'max_model_change':
        query_gain = compute_expected_model_change(query_state, spec_fsm)
        demonstration_gain = compute_expected_model_change_demonstrations(spec_fsm, pedagogical, selectivity)

    demo = True if demonstration_gain >= query_gain else False
    return demo, demonstration_gain, query_gain


def create_trial_directory(directory, i, conditions):

    n_conditions = len(conditions)

    trial_dir = os.path.join(directory, f'trial_{i}')
    if not os.path.exists(trial_dir):
        os.mkdir(trial_dir)

    for cid in range(len(conditions)):
        condition_path = os.path.join(trial_dir, f'condition_{cid}')
        if not os.path.exists(condition_path):
            os.mkdir(condition_path)
            os.mkdir(os.path.join(condition_path, global_params.raw_data_path))
            os.mkdir(os.path.join(condition_path, global_params.compressed_data_path))
            os.mkdir(os.path.join(condition_path, global_params.distributions_path))


def write_run_data_new(out_data, run_id, typ):
    if not os.path.exists(os.path.join(global_params.results_path,'Runs')): os.mkdir(os.path.join(global_params.results_path,'Runs'))
    filename = os.path.join(global_params.results_path, 'Runs', f'{typ}_Run_{run_id}.pkl')
    #out_data['Queries'] = [q['trace'] for q in out_data['Queries']]
    with open(filename, 'wb') as file:
        dill.dump(out_data, file)



def ground_truth_selector(demo_directory, demo = 2, ground_truth_formula = None, p_threats=0.5, p_waypoints = 0.5, p_orders = 0.5):
    if ground_truth_formula == None:
        ground_truth_formula = sample_ground_truth(threats = True, p_threats = p_threats, p_waypoints = p_waypoints, p_orders = p_orders)

    if type(demo) == int:
        n_demo = demo
        eval_agent = create_demonstrations(ground_truth_formula, n_demo, demo_directory)
    else:
        n_demo = len(demo.episodic_record)
        record_agent_episodes(demo, demo_directory)
        eval_agent = deepcopy(demo)
    return n_demo, eval_agent, ground_truth_formula

def record_agent_episodes(eval_agent, demo_directory):
    MDP = eval_agent.MDP
    for record in eval_agent.episodic_record:

        trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
        trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

        new_traj = create_query_demo(trace_slices)

        write_demo_query_data(new_traj, True, demo_directory, filename='demo')

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
    #data['Queries'] = [q['trace'] for q in data['Queries']]

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
            visualize_query(data['Queries'][i]['trace'])
            type = data['Queries'][i]['type']
            label = data['Queries'][i]['label']
            plt.title(f'{type} {i+1}: {label}')
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

def create_demonstrations(formula, nDemo, demo_directory,  verbose = True, n_threats = 0):

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

        write_demo_query_data(new_traj, True, demo_directory, filename='demo')
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

def run_trial(trial_config):
    args = trial_config.args
    command_headers = trial_config.command_headers
    conditions = trial_config.conditions

    batches = trial_config.batches
    n_demo = trial_config.n_demo
    n_query = trial_config.n_query
    workers = trial_config.workers
    mode = trial_config.mode
    p_threats = trial_config.p_threats
    p_orders = trial_config.p_orders
    p_waypoints = trial_config.p_waypoints


    global_params.results_path = trial_config.result_path
    check_results_path(global_params.results_path)
    results = run_parallel_trials(args, command_headers, conditions, batches = batches, workers = workers, n_demo = n_demo, n_query = n_query,
    given_ground_truth = None, p_threats = p_threats, p_waypoints = p_waypoints, p_orders = p_orders,
    mode = mode)



if __name__ == '__main__':

    import trial_config2, trial_config1
    from meta_analysis import *

    for trial_config in [trial_config2]:
        run_trial(trial_config)
        directory = trial_config.result_path
        data = read_data(directory)
        results = get_similarities(data, format = 'queries')
        plot_similarities_mean(directory, data)
        plot_similarities_median(directory, data)
        plot_similarities_box(directory, data)
        plot_similarities_CI(directory, data)

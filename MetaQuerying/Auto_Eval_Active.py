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
import auto_eval_params as params
import os
import json
from copy import deepcopy


def run_paired_trials(trials = 200, n_demo = 2, n_query = 4, ground_truth_formula = None, mode = 'incremental'):

    #Making this incremental
    #Check if the results path already exists
    summary_file = os.path.join(params.results_path,'paired_summary.pkl')
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
        n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo=n_demo, ground_truth_formula = ground_truth_formula)
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
    #
    summary_file = os.path.join(params.results_path,'paired_summary.pkl')
    with open(summary_file,'wb') as file:
        dill.dump(out_data,file)



    #Write to file in results path and return
    return out_data





def run_meta_selection_trials(demo = 2, n_query = 4, query_strategy = 'info_gain',
run_id = 1, ground_truth_formula = None, write_file = True, verbose=True):

    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0
    queries_performed = 0
    demonstrations_requested = 0

    clear_demonstrations(params)
    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
            Distributions.append(extract_dist(MDPs[-1]))
        else:
            #learn from an active info gain query
            if verbose: print(f'Trial {run_id}: Selecting Query for next data point')
            queries_performed = queries_performed + 1

            #Create the query
            if verbose: print(f'Trial {run_id}: Generating query {i+1} demo')
            Queries.append(create_active_query(MDPs[-1], verbose=verbose, non_terminal = params.non_terminal, query_strategy = query_strategy))

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
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
        write_run_data_new(out_data, run_id, typ = f'Active_{query_strategy}')
    return out_data

def run_batch_trial(demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None, mode = 'incremental', write_file = True, verbose=True):

    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0

    clear_demonstrations(params)

    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo, ground_truth_formula)

    if mode == 'incremental':


        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
            infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
            returnval = os.system(infer_command)
            if returnval: Exception('Inference failure')

            # Recompile the MDP with the updated specification and add the distributions
            spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
            MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
            write_demo_query_data(new_traj, True, params.compressed_data_path, filename = 'demo')

        # Run batch Inference
        infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo + n_query}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference Failure')

        # Compile the first MDP
        spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
    return out_data

def run_active_trial(query_strategy = 'uncertainty_sampling', demo = 2, n_query = 4, run_id = 1, ground_truth_formula = None,
verbose = True, write_file = True):

    MDPs = []
    Distributions = []
    Queries = []
    query_mismatches = 0

    clear_demonstrations(params)

    print(f'Trial {run_id}: Running Active trial {query_strategy}')

    n_demo, eval_agent, ground_truth_formula = ground_truth_selector(demo, ground_truth_formula)

    # Run batch Inference
    infer_command = f'webppl batch_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nTraj {n_demo}'
    returnval = os.system(infer_command)
    if returnval: Exception('Inference Failure')

    # Compile the first MDP
    spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
    MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
    Distributions.append(extract_dist(MDPs[-1],))

    #For the number of budgeted Queries
    for i in range(n_query):

        #Check for mismatch between info gain and uncertainty Sampling
        uncertainty_sampling_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type = 'uncertainty_sampling')
        infogain_desired_state, _ = identify_desired_state(MDPs[-1].specification_fsm, query_type='info_gain')
        if uncertainty_sampling_desired_state != infogain_desired_state: query_mismatches = query_mismatches + 1

        #Create the query
        if verbose: print(f'Trial {run_id}: Generating query {i+1} demo')
        Queries.append(create_active_query(MDPs[-1], verbose=verbose, non_terminal = params.non_terminal, query_strategy = query_strategy))

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
        infer_command = f'webppl active_bsi.js --require webppl-json --require webppl-fs -- --nSamples {params.n_samples}  --nBurn {params.n_burn} --dataPath \'{params.compressed_data_path}\' --outPath \'{params.distributions_path}\' --nQuery {i+1}'
        returnval = os.system(infer_command)
        if returnval: Exception('Inference failure')

        # Recompile the MDP with the updated specification and add the distributions
        spec_file = spec_file = os.path.join(params.distributions_path, 'batch_posterior.json')
        MDPs.append(CreateSpecMDP(spec_file, n_threats = 0, n_waypoints = params.n_waypoints))
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
    return out_data


def write_run_data_new(out_data, run_id, typ):
    if not os.path.exists(os.path.join(params.results_path,'Runs')): os.mkdir(os.path.join(params.results_path,'Runs'))
    filename = os.path.join(params.results_path, 'Runs', f'{typ}_Run_{run_id}.pkl')
    with open(filename, 'wb') as file:
        dill.dump(out_data)



def ground_truth_selector(demo = 2, ground_truth_formula = None):
    if ground_truth_formula == None:
        ground_truth_formula = sample_ground_truth()

    if type(demo) == int:
        n_demo = demo
        eval_agent = create_demonstrations(ground_truth_formula, n_demo)
    else:
        n_demo = len(demo.episodic_record)
        record_agent_episodes(demo)
        eval_agent = deepcopy(demo)
    return n_demo, eval_agent, ground_truth_formula

def record_agent_episodes(eval_agent):
    MDP = eval_agent.MDP
    for record in eval_agent.episodic_record:

        trace_slices = [MDP.control_mdp.create_observations(rec[0][1]) for rec in record]
        trace_slices.append(MDP.control_mdp.create_observations(record[-1][2][1]))

        new_traj = create_query_demo(trace_slices)

        write_demo_query_data(new_traj, True, params.compressed_data_path, filename='demo')

def write_run_data(Distributions, MDPs, Queries, ground_truth_formula, run_id, type = 'Active'):
    if not os.path.exists(os.path.join(params.results_path,'Runs')): os.mkdir(os.path.join(params.results_path,'Runs'))
    filename = os.path.join(params.results_path, 'Runs', f'{type}_Run_{run_id}.pkl')
    data = {}
    data['Distributions'] = Distributions
    data['MDPs'] = MDPs
    data['Queries'] = [q['trace'] for q in Queries]
    data['True_Formula'] = ground_truth_formula

    with open(filename,'wb') as file:
        dill.dump(data, file)

def create_run_log(run_id, type = 'Active'):
    filename = os.path.join(params.results_path, 'Runs', f'{type}_Run_{run_id}')
    with open(filename+'.pkl','rb') as file:
        data = dill.load(file)

    if type == 'Batch':
        n_demo = params.n_demo + params.n_queries
    else:
        n_demo = params.n_demo

    pdf_file = filename+'.pdf'
    with PdfPages(pdf_file) as pdf:
        #print the ground truth formula
        plt.figure()
        true_form = json.dumps(data['True_Formula'])
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

def create_demonstrations(formula, nDemo, verbose = True, n_threats = 0):

    specification_fsm = SpecificationFSM(formulas=[formula], probs = [1])
    control_mdp = SyntheticMDP(0,params.n_waypoints)
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



def report_entropies(typ = None):
    if typ == None:
        types = ['Active','Batch','Random', 'Base']
    elif type(typ) == list:
        types = typ
    else:
        types = [typ]


    filename = os.path.join(params.results_path, 'paired_summary.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)

    Entropies = {}
    Entropies['individual'] = {}
    Entropies['average'] = {}

    for typ in types:
        Entropies['individual'][typ] = data[typ]['entropies']
        Entropies['average'][typ] = np.mean(data[typ]['entropies'])

    Entropies = pd.DataFrame(Entropies['individual'])
    return Entropies

def report_map_similarities(typ=None):
    if typ == None:
        types = ['Active','Batch','Random', 'Base']
    elif type(typ) == list:
        types = typ
    else:
        types = [typ]

    similarities = {}
    similarities['individual'] = {}
    similarities['average'] = {}

    filename = os.path.join(params.results_path, 'paired_summary.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)

    for typ in types:
        similarities['individual'][typ] = [compare_formulas(f1, f2) for (f1,f2)
                        in zip(data['true_formulas'], data[typ]['map_formulas'])]
        similarities['average'][typ] = np.mean(similarities['individual'][typ])

    similarities = pd.DataFrame(similarities['individual'])

    return similarities

def report_similarities(typ=None):
    if typ == None:
        types = ['Active','Batch','Random', 'Base']
    elif type(typ) == list:
        types = typ
    else:
        types = [typ]

    similarities = {}
    similarities['individual'] = {}
    similarities['average'] = {}

    filename = os.path.join(params.results_path, 'paired_summary.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)

    for typ in types:
        similarities['individual'][typ] = [compare_distribution(f1,d) for
                    (f1,d) in zip(data['true_formulas'], data[typ]['dists'])]
        similarities['average'][typ] = np.mean(similarities['individual'][typ])

    similarities = pd.DataFrame(similarities['individual'])
    return similarities

def assimilate_metrics(typ):
    Entropy = report_entropies(typ)
    Similarity = report_similarities(typ)

    data = {}
    for i in Entropy.index:
        for column in   Entropy.columns:
            ids = len(data)
            data[ids] = {}
            data[ids]['Entropy'] = Entropy.loc[i, column]
            data[ids]['Similarity'] = Similarity.loc[i, column]
            data[ids]['type'] = column
            data[ids]['n_data'] = params.n_queries + params.n_demo

    data = pd.DataFrame.from_dict(data, orient='index')
    data.reset_index()
    return data


def get_summary():
    with open(os.path.join(params.results_path, 'paired_summary.pkl'),'rb') as file:
        data = dill.load(file)
    return data

def get_run_data(i=0, run_type = 'Active'):
    filename = os.path.join(params.results_path, 'Runs',f'{run_type}_Run_{i}.pkl')
    with open(filename, 'rb') as file:
        run_data = dill.load(file)
    return run_data

def create_results_path():
    if not os.path.exists(params.results_path):
        os.mkdir(params.results_path)
        os.mkdir(os.path.join(params.results_path, 'Runs'))

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
    params.results_path = '/home/ajshah/Results/Test_Meta'
    check_results_path(params.results_path)
    n_trials = 1
    n_demo = 2
    n_query = 1

    results = run_paired_trials(trials = n_trials, n_demo = n_demo, n_query = n_query)


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

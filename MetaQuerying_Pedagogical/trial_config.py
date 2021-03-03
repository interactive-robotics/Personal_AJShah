



#trial_functions = [run_active_trial, run_active_trial, run_batch_trial, run_meta_selection_trials, run_pedagogical_trials]
conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Batch', 'Meta-Selection', 'Pedagogical Batch', 'Meta Pedagogical']


args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
args3 = {'n_query': n_query, 'mode': mode}
args4 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling'}
args5 = {'n_query': n_query,}
args6 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'pedagogical': True}
args = [args1, args2, args3, args4, args5, args6]



command_headers = [f'python active_trial.py',
            f'python active_trial.py',
            f'python batch_trial.py',
            f'python meta_trial.py',
            f'python pedagogical_trial.py',
            f'python meta_trial.py']

batches = 200
n_demo = 7
n_queries = 1

result_path = f'/home/ajshah/Results/Test_Meta'
#result_path = f'/home/ajshah/Results/Results_{n_data}_pedagogical2'

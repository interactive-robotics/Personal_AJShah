batches = 200
workers = 2
n_demo = 2
n_query = 3
mode = 'incremental'

conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Batch', 'Meta-Selection', 'Pedagogical Batch', 'Meta Pedagogical']
#conditions = ['A','B','C','D','E','F']

args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
args3 = {'n_query': n_query, 'mode': mode}
args4 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling'}
args5 = {'n_query': n_query,}
args6 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'pedagogical': True, 'selectivity': None}
args = [args1, args2, args3, args4, args5, args6]



command_headers = [f'python active_trial.py',
            f'python active_trial.py',
            f'python batch_trial.py',
            f'python meta_trial.py',
            f'python pedagogical_trial.py',
            f'python meta_trial.py']


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_{n_data}_pedagogical'

######## Comparison between active acquisition functions ########

batches = 30
workers = 2
n_demo = 2
n_query = 10
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Model Change Pedagogical', 'Model Change Noisy Pedagogical 0.1', 'Model Change Noise Pedagogical 1', 'Model Change 1', 'Model Change 2'
              'Info Gain Pedagogical', 'Info Gain Noisy Pedagogical 0.1', 'Info Gain Noisy Pedagogical 1', 'Info Gain 1', 'Info Gain 2']

args = []
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 1})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 5})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': False})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 1})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 5})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': False, 'selectivity': 0})

#args = [args1, args2, args3, args4]



command_headers = [f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py'
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Meta_Trials'

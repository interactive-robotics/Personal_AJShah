######## Comparison between active acquisition functions ########

batches = 250
workers = 2
n_demo = 2
n_query = 10
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Meta Model Change', 'Meta Info Gain', 'Meta Uncertainty', 'Meta Model Change Pedagogical', 'Meta Info Gain Pedagogical', 'Meta Uncertainty Pedagogical']


args = []
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'uncertainty_sampling', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True})
args.append({'n_query': n_query, 'query_strategy': 'info_gain', 'meta_policy': 'info_gain', 'pedagogical': True})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'uncertainty_sampling', 'pedagogical': True,})

#args = [args1, args2, args3, args4]



command_headers = [f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Meta_Comparison'

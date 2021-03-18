######## Comparison between active acquisition functions ########

batches = 50
workers = 2
n_demo = 2
n_query = 13
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Pedagogical', 'Noisy Pedagogical 1', 'Noisy Pedagogical 5', 'Non Pedagogical',
              'Meta Pedagogical', 'Meta Noisy Pedagogical 1', 'Meta Noisy Pedagogical 5', 'Meta Non Pedagogical']

args = []
args.append({'n_query': n_query, })
args.append({'n_query': n_query, 'selectivity': 1})
args.append({'n_query': n_query, 'selectivity': 5})
args.append({'n_query': n_query,})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 1})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 5})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': False})

#args = [args1, args2, args3, args4]



command_headers = [f'python batch_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Meta_Batch_Comparison'
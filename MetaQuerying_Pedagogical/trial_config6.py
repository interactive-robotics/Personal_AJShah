######## Comparison between active acquisition functions ########

batches = 30
workers = 2
n_demo = 2
n_query = 10
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Non Pedagogical 1', 'Non Pedagogical 2', 'Noisy Pedagogical 0.01', 'Noisy Pedagogical 0.1', 'Pedagogical',
              'Meta Non Pedagogical 1', 'Meta Non Pedagogical 2', 'Meta Noisy Pedagogical 0.01', 'Meta Noisy Pedagogical 0.1', 'Meta Pedagogical']

args = []
args.append({'n_query': n_query, 'selectivity': 0 })
args.append({'n_query': n_query,})
args.append({'n_query': n_query, 'selectivity': 0.1})
args.append({'n_query': n_query, 'selectivity': 0.01})
args.append({'n_query': n_query,})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': False,})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 0.01})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': 0.1})
args.append({'n_query': n_query, 'query_strategy': 'max_model_change', 'meta_policy': 'max_model_change', 'pedagogical': True,})

#args = [args1, args2, args3, args4]



command_headers = [f'python pedagogical_trial.py',
            f'batch_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Meta_Batch_Comparison'

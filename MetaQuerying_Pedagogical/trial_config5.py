######## Comparison between active acquisition functions ########

batches = 50
workers = 2
n_demo = 2
n_query = 13
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Non Pedagogical', 'Noisy Pedagogical 0.1', 'Noisy Pedagogical 0.5', 'Noisy Pedagogical 1', 'Noisy Pedagogical 5', 'Pedagogical',]

args = []
args.append({'n_query': n_query, 'selectivity': 0 })
args.append({'n_query': n_query, 'selectivity': 0.1})
args.append({'n_query': n_query, 'selectivity': 0.5})
args.append({'n_query': n_query, 'selectivity': 1})
args.append({'n_query': n_query, 'selectivity': 5})
args.append({'n_query': n_query,})


#args = [args1, args2, args3, args4]



command_headers = [f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            f'python pedagogical_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Batch_Noise2'

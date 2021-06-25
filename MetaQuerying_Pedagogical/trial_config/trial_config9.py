######## Comparison between active acquisition functions ########

batches = 250
workers = 2
n_demo = 2
n_query = 8
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Anchoring -5', 'Anchoring -1', 'Non Pedagogical', 'Noisy Pedagogical 1', 'Noisy Pedagogical 5', 'Pedagogical',]

args = []
args.append({'n_query': n_query, 'selectivity': -5})
args.append({'n_query': n_query, 'selectivity': -1 })
args.append({'n_query': n_query, 'selectivity': 0})
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
result_path = f'/home/ajshah/Results/Batch_Noise'

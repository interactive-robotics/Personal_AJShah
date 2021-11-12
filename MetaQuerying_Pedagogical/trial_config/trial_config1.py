######## Comparison between active acquisition functions ########

batches = 1
workers = 10
n_demo = 4
n_query = 2
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5
k = 1

conditions = ['Uncertainty Sampling', 'Info Gain', 'Model Change', 'Uncertainty Sampling top-2', 'Info Gain top-2', 'Model Change top-2',]

args = []
args.append({'n_query': n_query, 'k':1, 'query_strategy': 'uncertainty_sampling',})
args.append({'n_query': n_query, 'k':1, 'query_strategy': 'info_gain',})
args.append({'n_query': n_query, 'k':1, 'query_strategy': 'max_model_change'})
args.append({'n_query': n_query, 'k':2, 'query_strategy': 'uncertainty_sampling',})
args.append({'n_query': n_query, 'k':2, 'query_strategy': 'info_gain',})
args.append({'n_query': n_query, 'k':2, 'query_strategy': 'max_model_change'})






command_headers = [f'python active_trial.py',
            f'python active_trial.py',
            f'python active_trial.py',
            f'python active_trial.py',
            f'python active_trial.py',
            f'python active_trial.py',
        ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/users/ashah137/scratch/Results_Meta_Puns'

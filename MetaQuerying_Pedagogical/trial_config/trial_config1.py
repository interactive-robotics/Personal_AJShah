######## Comparison between active acquisition functions ########

batches = 50
workers = 2
n_demo = 2
n_query = 8
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Active: Uncertainty Sampling', 'Active: Info Gain', 'Active: Model Change']

args1 = {'n_query': n_query, 'query_strategy': 'uncertainty_sampling',}
args2 = {'n_query': n_query, 'query_strategy': 'info_gain',}
args3 = {'n_query': n_query, 'query_strategy': 'max_model_change'}

args = [args1, args2, args3]



command_headers = [f'python active_trial.py',
            f'python active_trial.py',
            f'python active_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Active2'

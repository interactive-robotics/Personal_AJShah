######## Comparison between active acquisition functions ########

batches = 50
workers = 2
n_demo = 2
n_query = 10
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Demo : Optimal, Model: -5','Demo : Optimal, Model: 0','Demo : Optimal, Model: 5', 'Demo : Optimal, Model: Optimal']

args = []
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': None, 'demonstrator_selectivity': -5})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': None, 'demonstrator_selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': None, 'demonstrator_selectivity': 5})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'max_model_change', 'pedagogical': True, 'selectivity': None, 'demonstrator_selectivity': None})
#args = [args1, args2, args3, args4]



command_headers = [
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Meta_Selectivity_Optimal'

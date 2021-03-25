######## Comparison between active acquisition functions ########

batches = 30
workers = 2
n_demo = 2
n_query = 10
mode = 'incremental'
p_threats = 0.5
p_waypoints = 0.5
p_orders = 0.5

conditions = ['Meta Anchored -1', 'Meta Anchored -0.1', 'Meta Non Pedagogical', 'Meta Noisy Pedagogical 0.1',
            'Meta Noisy Pedagogical 1', 'Meta Pedagogical']

args = []
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': -1})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': -0.1})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 0})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 0.1})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True, 'selectivity': 1})
args.append({'n_query': n_query, 'query_strategy': 'uncertainty_sampling', 'meta_policy': 'info_gain', 'pedagogical': True})
#args = [args1, args2, args3, args4]



command_headers = [
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',
            f'python meta_trial.py',           
            ]


n_data = n_demo + n_query

#result_path = f'/home/ajshah/Results/Test_Custom'
result_path = f'/home/ajshah/Results/Results_15_Meta_Noise'

import os
# Proposition parameters
n_waypoints = 5

# File paths
results_path = '/home/ajshah/Results/Results_5_with_baseline'
#if not os.path.exists(results_path):
#    os.mkdir(results_path)
#    os.mkdir(os.path.join(results_path, 'Runs'))
data_path = 'Data'
raw_data_path = data_path+'/RawData'
compressed_data_path = data_path + '/CompressedData'
distributions_path = data_path + '/Distributions'

# Inference parameters
n_samples = 20000
n_burn = 100

# Run configuration parameters
n_runs = 200
n_demo = 2
n_queries = 3

# Query related parameters
non_terminal = True

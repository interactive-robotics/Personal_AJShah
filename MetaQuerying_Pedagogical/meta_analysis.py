from Auto_Eval_Active import *
import dill
import pandas as pd
import numpy as np
import seaborn as sns
from itertools import product
import math

def read_data(direc, file = 'paired_summary.pkl'):
    with open(os.path.join(direc, file), 'rb') as file:
        data = dill.load(file)
    return data

def pad_data(data):

    print('Padding Queries')
    conditions = list(data['results'][0].keys())
    conditions.remove('ground_truth')

    queries = [len(data['results'][i][c]) for (i,c) in product(data['results'].keys(), conditions)]
    n_queries = np.max(queries)


    for i in tqdm(data['results'].keys()):
        for c in conditions:
            if len(data['results'][i][c]) < n_queries:
                last_dist = data['results'][i][c][-1]
                data['results'][i][c].extend([last_dist]*(n_queries - len(data['results'][i][c])))
    return data

def get_similarities(data, format = 'long'):

    conditions = list(data['results'][0].keys())
    conditions.remove('ground_truth')

    trials = len(data['results'])
    queries = len(data['results'][0][conditions[0]])

    results = {}

    if format == 'condition':

        for c in conditions:
            results[c] = {}
            for t in range(trials):
                results[c][t] = {}
                for q in range(queries):
                    results[c][t][q] = compare_distribution(data['results'][t]['ground_truth'], data['results'][t][c][q])

            results[c] = pd.DataFrame.from_dict(results[c], orient = 'index')

    if format == 'queries':

        for q in range(queries):
            results[q] = {}
            for t in range(trials):
                results[q][t] = {}
                for c in conditions:
                    results[q][t][c] = compare_distribution(data['results'][t]['ground_truth'], data['results'][t][c][q])

            results[q] = pd.DataFrame.from_dict(results[q], orient = 'index')

    if format == 'long':

        idx = 0
        results = {}
        for t in range(trials):
            for c in conditions:
                for q in range(len(data['results'][t][c])):
                    results[idx] = {}
                    results[idx]['Similarity'] = compare_distribution(data['results'][t]['ground_truth'], data['results'][t][c][q])
                    results[idx]['Condition'] = c
                    results[idx]['Data Points'] = 2 + q
                    idx = idx + 1

        results = pd.DataFrame.from_dict(results, orient = 'index')

    return results

def extract_selectivity(condition):
    if 'Meta' in condition:
        protocol = 'Meta-Selection'
    else:
        protocol = 'Demonstrations'

    if condition in ['Meta Pedagogical', 'Pedagogical']:
        selectivity = math.nan
    elif condition in ['Meta Non Pedagogical', 'Non Pedagogical']:
        selectivity = 0
    else:
        selectivity = float(condition.split()[-1])

    return (protocol, selectivity)

def create_sims_table(sims, sim_key):
    #Assume sims in long format

    out_table = {}
    for idx in sims.index:
        (protocol, selectivity) = extract_selectivity(sims[sel].loc[idx]['Condition'])
        out_table[idx] = {}
        out_table[idx]['Similarity'] = sims.loc[idx]['Similarity']
        out_table[idx]['Condition'] = protocol
        out_table[idx]['Selectivity'] = selectivity
        out_table[idx]['Data Points'] = sims.loc[idx]['Data Points']
    out_table = pd.DataFrame.from_dict(out_table, orient = 'index')
    max_selectivity = np.nanmax(sims['Similarity'])
    out_table.fillna(max_selectivity+1, inplace=True)
    return out_table


def create_mismatch_table():
    directory =  'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'

    sims = {}

    for (filename,sel) in zip(['model_neg5_summary.pkl', 'model_0_summary.pkl', 'model_optimal_summary.pkl'],[-5,0,5]):
        with open(os.path.join(directory, filename),'rb') as file:
            data = dill.load(file)
        data = pad_data(data)
        sims[sel] = get_similarities(data)

    idx = 0
    data = {}
    for sel in [-5,0,5]:
        for i in sims[sel].index:

            data[idx] = {}
            data[idx]['Similarity'] = sims[sel].loc[i,'Similarity']

            if sims[sel].loc[i,'Condition'].split()[-1] == 'Optimal':
                demonstrator_sel = 6
            else:
                demonstrator_sel = int(sims[sel].loc[i,'Condition'].split()[-1])


            data[idx]['Demonstrator Selectivity'] = demonstrator_sel
            data[idx]['Model Selectivity'] = sel
            data[idx]['Data Points'] = sims[sel].loc[i,'Data Points']
            idx=idx+1

    return pd.DataFrame.from_dict(data, orient = 'index')




def plot_similarities_mean(directory, results ,savename = 'similarity.png'):
    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def plot_similarities_median(directory, results ,savename = 'similarity_median.png'):
    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def plot_similarities_box(directory, results ,savename = 'similarity_box.png'):
    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.boxplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', showfliers = False, whis = 0)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def plot_similarities_quantitative(sims):
    from sns_defaults import rc
    with sns.plotting_context('poster', rc=rc):
        plt.figure(figsize=[24,9])
        sns.lineplot(data = sims, x = 'Data Points', y = 'Similarity', hue = 'Selectivity', style='Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)

def create_quantile_estimator(q):

    def estimator(data):
        return np.quantile(data, q)

    return estimator

def plot_similarities_CI(directory, results, savename = 'similarity_range.png'):

    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = None, alpha = 0.85)
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = create_quantile_estimator(0.3), ci = None, alpha = 0.3, legend = False)
        #sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        #err_kws = {'capsize':10, 'capthick':3}, estimator = create_quantile_estimator(0.9), ci = 95, alpha = 0.3)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')


# with sns.plotting_context('poster', rc = {'axes.labelsize': 28, 'axes.titlesize': 32, 'legend.fontsize': 24, 'xtick.labelsize': 24, 'ytick.labelsize': 22}):
#         with sns.color_palette('dark'):
#             plt.figure(figsize=[12,9])
#             #sns.boxplot(data = all_data, x = 'n_data', y = 'Entropy', hue = 'type')
#             #sns.barplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'type', estimator = np.mean, capsize = 0.05, ci = 95, alpha = 0.85)
#             sns.lineplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'Protocol', err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
#             plt.title('Mean Entropy', )
#             plt.xlabel('Number of task executions')
#             plt.legend(loc='upper right')
#             plt.savefig(os.path.join(params.results_path,'..','Entropy.png'), dpi = 500, bbox_inches = 'tight')


if __name__ == '__main__':

#    directory = f'/home/ajshah/Results/Results_15_meta_sampler_no_threats'
    directory = f'/home/ajshah/Results/Results_15_Active3'
    data = read_data(directory)
    data = pad_data(data)
    results = get_similarities(data, format = 'long')
    plot_similarities_mean(directory, results)
    plot_similarities_median(directory, results)
    plot_similarities_box(directory, results)
    plot_similarities_CI(directory, results)

    # type_key ={
    #     'Anchored -1': ('Demonstrations', -1),
    #     'Non Pedagogical': ('Demonstrations', 0),
    #     'Noisy Pedagogical 1': ('Demonstrations', 1),
    #     'Pedagogical': ('Demonstrations', 2),
    #     'Meta Anchored -1': ('Meta-Selection', -1),
    #     'Meta Non Pedagogical 0': ('Meta-Selection', 0),
    #     'Meta Noisy Pedagogical 1': ('Meta-Selection', 1),
    #     'Meta Pedagogical': ('Meta-Selection', 2)}

    # sims = get_similarities(data)
    # sims = create_sims_table(sims, type_key)

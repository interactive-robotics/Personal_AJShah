from Auto_Eval_Active import *
import dill
import pandas as pd
import numpy as np
import seaborn as sns

def read_data(direc):
    with open(os.path.join(direc, 'paired_summary.pkl'), 'rb') as file:
        data = dill.load(file)
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
            for q in range(queries):
                for c in conditions:
                    results[idx] = {}
                    results[idx]['Similarity'] = compare_distribution(data['results'][t]['ground_truth'], data['results'][t][c][q])
                    results[idx]['Condition'] = c
                    results[idx]['Data Points'] = 2 + q
                    idx = idx + 1

        results = pd.DataFrame.from_dict(results, orient = 'index')

    return results

def plot_similarities_mean(directory, data ,savename = 'similarity.png'):
    results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def plot_similarities_median(directory, data ,savename = 'similarity_median.png'):
    results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.lineplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def plot_similarities_box(directory, data ,savename = 'similarity_box.png'):
    results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [48,18])
        sns.boxplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', showfliers = False, whis = 0)
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')

def create_quantile_estimator(q):

    def estimator(data):
        return np.quantile(data, q)
    
    return estimator

def plot_similarities_CI(directory, data, savename = 'similarity_range.png'):

    results = get_similarities(data, format = 'long')
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
    directory = f'/home/ajshah/Results/Results_15_Batch_Noise'
    data = read_data(directory)
    results = get_similarities(data, format = 'queries')
    plot_similarities_mean(directory, data)
    plot_similarities_median(directory, data)
    plot_similarities_box(directory, data)
    plot_similarities_CI(directory, data)




from Auto_Eval_Active import *
import dill
import pandas as pd
import numpy as np
import seaborn as sns
from itertools import product
import math
from scipy.stats import entropy
from tqdm import tqdm
import matplotlib as mpl

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

def get_entropies(data):
    
    conditions = list(data['results'][0].keys())
    conditions.remove('ground_truth')
    trials = len(data['results'])
    queries = len(data['results'][0][conditions[0]])
    
    idx = 0
    results = {}
    for t in range(trials):
        for c in conditions:
            for q in range(len(data['results'][t][c])):
                results[idx] = {}
                results[idx]['Entropy'] = entropy(data['results'][t][c][q]['probs'])
                results[idx]['Condition'] = c
                results[idx]['Data Points'] = 2+q
                idx = idx+1
    results = pd.DataFrame.from_dict(results, orient = 'index')
    return results

def create_key_table(data = None, key = 'query_flags'):
    if data == None:
        directory = 'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'
        data = read_data(directory, file = 'active_summary2.pkl')
        data = pad_data(data)
    

    flags = data[key]
    conditions = flags[0].keys()
    out_data = {}
    counts = {}
    idx = 0

    for c in conditions:
        out_data[c] = {}
        for t in flags.keys():
            out_data[c][t] = {}
            for i in range(len(flags[t][c])):

                out_data[c][t][i] = flags[t][c][i]


        out_data[c] = pd.DataFrame.from_dict(out_data[c], orient = 'index')
        counts[c] = pd.DataFrame()
        for x in out_data[c].columns:
            counts[c][x] = out_data[c][x].value_counts()
    return counts

def plot_query_key(data = None, key = 'query_flags'):
    counts = create_key_table(data, key)
    from sns_defaults import rc

    for c in counts.keys():
        plot_frame = counts[c].transpose()
        plot_frame[True] = plot_frame[True]/np.sum(counts[c],axis=0)
        plot_frame[False] = plot_frame[False]/np.sum(counts[c],axis=0)

        with sns.plotting_context('poster', rc=rc):
            plt.figure(figsize = [24,10])
            plot_frame.plot.bar(stacked = True, ax = plt.gca())
            plt.title(c)

def create_count_table_disambiguity(data, keys = ['Uncertainty Sampling','Info Gain','Model Change']):
    counts = {}
    raw_data = {}
    plot_frame = pd.DataFrame()
    for key in keys:
        raw_data[key] = {}
        idx = 0
        for run_id in tqdm(range(len(data['results']))):
        #for run_id in tqdm(range(5)):
            entry = {}
            for exec_id in range(len(data['labels'][run_id][key])):
                dist = data['results'][run_id][key][exec_id+1]
                fsm = SpecificationFSM(dist['formulas'], dist['probs'])
                degenerate_state = fsm.id2states[0]
                state,_ = identify_desired_state(fsm)
                
                #check if trivial
                if state != degenerate_state:    
                    try:
                        entry[exec_id] = data['labels'][run_id][key][exec_id]
                    except:
                        print('run id: ', run_id, ' key: ', key, ' Exec_id: ', exec_id)
                else:
                    entry[exec_id] = None
            raw_data[key][run_id] = entry
            #idx = idx+1
        raw_data[key] = pd.DataFrame.from_dict(raw_data[key], orient='index')
        counts[key] = pd.DataFrame()
        for c in raw_data[key].columns:
            counts[key][c] = raw_data[key][c].value_counts()
        
        plot_frame[key] = counts[key].loc[True]/np.sum(counts[key],axis=0)
    return plot_frame
                
    
    




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

def create_sims_table(sims):
    #Assume sims in long format

    out_table = {}
    for idx in sims.index:
        (protocol, selectivity) = extract_selectivity(sims.loc[idx]['Condition'])
        out_table[idx] = {}
        out_table[idx]['Similarity'] = sims.loc[idx]['Similarity']
        out_table[idx]['Condition'] = protocol
        out_table[idx]['Selectivity'] = selectivity
        out_table[idx]['Data Points'] = sims.loc[idx]['Data Points']
    out_table = pd.DataFrame.from_dict(out_table, orient = 'index')
    max_selectivity = np.nanmax(out_table['Selectivity'])
    out_table.fillna(max_selectivity+1, inplace=True)
    return out_table

def create_table(data, key = 'Similarity'):
    #Assume sims in long format
    sims = data
    out_table = {}
    for idx in sims.index:
        (protocol, selectivity) = extract_selectivity(sims.loc[idx]['Condition'])
        out_table[idx] = {}
        out_table[idx][key] = sims.loc[idx][key]
        out_table[idx]['Condition'] = protocol
        out_table[idx]['Selectivity'] = selectivity
        out_table[idx]['Data Points'] = sims.loc[idx]['Data Points']
    out_table = pd.DataFrame.from_dict(out_table, orient = 'index')
    max_selectivity = np.nanmax(out_table['Selectivity'])
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

def plot_batch_meta_comparison():

    directory =  'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'
    data = read_data(directory, file = 'comparison_summary.pkl')
    data = pad_data(data)
    sims = get_similarities(data)
    data = create_sims_table(sims)
    from sns_defaults import rc
    with sns.plotting_context('poster', rc=rc):
        plt.figure(figsize = [24,12])
        sns.lineplot(data = data, x = 'Data Points', y = 'Similarity', hue = 'Selectivity', style = 'Condition', err_style = 'bars',
        err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)




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

def plot_similarities_box(directory, results ,savename = 'similarity_box.png', figsize = [10,8]):
    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = figsize)
        sns.boxplot(data = results, x = 'Data Points', y = 'Similarity', hue = 'Condition', showfliers = False, whis = 0, saturation = 0.85, palette='deep')
        plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')
        
def plot_box(directory, results , figsize = [10,8], key = 'Similarity', palette = 'deep', hue = 'Condition'):
    savename = f'{key}_box.png'
    #results = get_similarities(data, format = 'long')
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = figsize)
        sns.boxplot(data = results, x = 'Data Points', y = key, hue = hue, showfliers = False, whis = 0, saturation = 0.85, palette=palette)
        #plt.savefig(os.path.join(directory, savename), dpi = 500, bbox_inches = 'tight')
        #return cbar
        

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
        
        

def plot_median_IQR(data, key = 'Similarity', savefig = False, savename = 'similarity.png', figsize = [10,8], group_var = 'Condition', palette = 'deep', lower_q = 0.25, upper_q = 0.75):
    
    # Get median values and the upper and lower ends of the error bars
    
    medians = data.groupby(['Data Points', group_var]).median()
    lower = data.groupby(['Data Points', group_var]).quantile(q = lower_q)
    upper = data.groupby(['Data Points', group_var]).quantile(q = upper_q)
    
    # Determine palette colors for each group_var value
    conditions = list(medians.loc[medians.index[0][0]].index)
    data_points = list(medians[key].loc[:,conditions[0]].index)
    colors = {}
    if type(palette) == str:
        cmap = sns.color_palette(palette, as_cmap = True)
    else:
        cmap = palette
        colorbar = False
    if type(cmap) == list: #This is a discrete list of colors
        # Assign colors in order and then cycle
        cmap = sns.color_palette(palette)
        colorbar = False
        for i,c in enumerate(conditions):
            idx = i%len(cmap)
            colors[c] = cmap[idx]
    elif type(cmap) == dict:
        colors = cmap
    else: #This is a continuous map
        #assume that conditions are numbers
        colorbar = True
        norm = mpl.colors.Normalize(np.min(conditions), np.max(conditions))
        colormap = plt.cm.ScalarMappable(norm, cmap = cmap)
        for c in conditions:
            colors[c] = colormap.to_rgba(c)
    
    #Plot the medians with sns without any error bars
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = figsize)
        sns.lineplot(data = data, x = 'Data Points', y = key, hue = group_var, ci = None, palette=palette, estimator = np.median)

        #Now plot only the error bars using plt.errorbars but with the predefined colors
        for c in conditions:
            med = medians[key].loc[:,c]
            up = upper[key].loc[:,c] - med
            low = med - lower[key].loc[:,c]
            err = np.array(pd.concat([low, up], axis=1)).transpose()
            plt.errorbar(data_points, med, err, fmt = 'none', ecolor = colors[c], capsize = 10, capthick = 2)
        
        # Now create the colorbar if required
        if colorbar:
            ax = plt.gca()
            ax.get_legend().remove()
            cbar = plt.colorbar(colormap, label = group_var)
            cbar.ax.set_yticks([-4,-2,0,2,4,6])
            cbar.ax.set_yticklabels(['-4','-2','0','2','4','inf'])

            

''' Create Thesis figures '''
directory = 'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary\\ThesisResults'

'''Active comparison plots'''
def load_active_data():
    #directory = 'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'
    filename = os.path.join(directory, 'active_summary.pkl')
    
    with open(filename, 'rb') as file:
        data = dill.load(file)
    data = pad_data(data)
    
    return data

def load_active_plot_frame():
    filename = os.path.join(directory, 'active_label_counts.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)
    plot_frame = data['plot_frame']
    
    idx = 0
    scale_frame = {}
    
    for i in plot_frame.index:
        for c in plot_frame.columns:
            scale_frame[idx] = {}
            entry = {}
            entry['Fraction Acceptable'] = plot_frame.loc[i,c]
            entry['Query ID'] = i+1
            entry['Condition'] = c
            scale_frame[idx] = entry
            idx = idx + 1
    scale_frame = pd.DataFrame.from_dict(scale_frame, orient = 'index')
    
    from sns_defaults import rc
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [10,8])
        sns.barplot(data = scale_frame, x = 'Query ID', y = 'Fraction Acceptable', hue = 'Condition',palette = 'deep', ci = None)
        plt.legend(loc = 'lower left')
    savefile = os.path.join(directory, 'ThesisFigs','active_acceptable.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    return scale_frame



def plot_active_similarity(data = None):
    
    #directory = 'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'
    
    if data == None:
        data = load_active_data()
    
    sims = get_similarities(data)
    
    conditions = ['Uncertainty Sampling','Info Gain', 'Model Change']
    sims = sims.loc[sims['Condition'].isin(conditions)]
    
    #Create the plot
    plot_median_IQR(sims, figsize = [24,9])
    
    #Save the figure
    save_dir = os.path.join(directory, 'ThesisFigs')
    savename = os.path.join(save_dir, 'active_similarity.png')
    plt.savefig(savename, dpi = 500, bbox_inches='tight')
    return sims

def plot_active_entropy(data = None):
    #directory = 'C:\\Users\\AJShah\\Documents\\GitHub\\Temporary'
    if data == None:
        data = load_active_data()
    entropy = get_entropies(data)
    
    conditions = ['Uncertainty Sampling', 'Info Gain', 'Model Change']
    entropy = entropy.loc[entropy['Condition'].isin(conditions)]
    
    #Create the plot
    plot_median_IQR(entropy, key = 'Entropy')
    
    #Save the plot
    save_dir = os.path.join(directory,'ThesisFigs')
    savename = os.path.join(save_dir, 'active_entropy.png')
    plt.savefig(savename, dpi=500, bbox_inches='tight')


'''batch noise plots'''

def load_batch_noise(key = 'Similarity'):
    filename = os.path.join(directory, 'Batch_noise_summary.pkl')
    with open(filename,'rb') as file:
        data = dill.load(file)
    data = pad_data(data)
    
    return data

from sns_defaults import rc

def plot_batch_noise_entropy(data = None):
    if data is None:
        data = load_batch_noise_sims()
    data = get_entropies(data)
    entropies = create_table(data, key = 'Entropy')
    
    plot_median_IQR(entropies, key = 'Entropy', group_var = 'Selectivity', palette = 'flare')
    ax = plt.gca()
    # Save the figure
    savefile = os.path.join(directory,'ThesisFigs','batch_noise_entropy.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    return entropies


def plot_batch_noise_similarity(data = None):
    if data is None:
        data = load_batch_noise()
    #Plot the figure
    
    data = get_similarities(data)
    sims = create_sims_table(data)
    
    plot_median_IQR(sims, group_var = 'Selectivity', palette = 'flare', figsize = [24,9])
    # Save the figure
    savefile = os.path.join(directory,'ThesisFigs','batch_noise_similarity.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    
'''Meta-Comparison plots'''
def load_meta_comparison_data():
    filename = os.path.join(directory, 'meta_comparison.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)
    data = pad_data(data)
    return data

def create_meta_comparison_palette():
    palette1 = sns.color_palette('dark',3)
    palette2 = sns.color_palette('muted',3)
    palette = {}
    
    palette['Meta Uncertainty'] = palette2[0]
    palette['Meta Uncertainty Pedagogical'] = palette1[0]
    
    palette['Meta Info Gain'] = palette2[1]
    palette['Meta Info Gain Pedagogical'] = palette1[1]
    
    palette['Meta Model Change Pedagogical'] = palette1[2]
    palette['Meta Model Change'] = palette2[2]
    return palette
    

def filter_sims(sims, conditions):
    filtered_sims = sims.loc[sims['Condition'].isin(conditions),:]
    return filtered_sims

def plot_meta_comparison_similarity(data=None):
    if data is None:
        data = load_meta_comparison_data()
    
    sims = get_similarities(data)
    
    query_strats = ['Meta Uncertainty', 'Meta Info Gain', 'Meta Model Change']
    palette = create_meta_comparison_palette()
    
    for q in query_strats:
        conditions = [q,q+' Pedagogical']
        filtered_sims = filter_sims(sims, conditions)
        plot_median_IQR(filtered_sims, group_var = 'Condition', key = 'Similarity', palette = palette)
        plt.legend(fontsize=18)
        #Save the figure
        q_string = q.replace(' ','_')
        savefile = os.path.join(directory,'ThesisFigs',f'meta_comparison_similarity_{q_string}.png')
        plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
        
    
    
    
    

def plot_meta_comparison_entropy(data=None):
    if data is None:
        data = load_meta_comparison_data()
    entropies = get_entropies(data)
    
    query_strats = ['Meta Uncertainty', 'Meta Info Gain', 'Meta Model Change']
    palette = create_meta_comparison_palette()
    
    for q in query_strats:
        conditions = [q,q+' Pedagogical']
        filtered_sims = filter_sims(entropies, conditions)
        plot_median_IQR(filtered_sims, group_var = 'Condition', key = 'Entropy', palette = palette)
        plt.legend(fontsize=18)
        #Save the figure
        q_string = q.replace(' ','_')
        savefile = os.path.join(directory,'ThesisFigs',f'meta_comparison_entropy_{q_string}.png')
        plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    
def plot_meta_comparison_demo_counts(data = None, conditions = None):
    if data is None:
        data = load_meta_comparison_data()
    
    table = create_key_table(data, key = 'meta_selections')
    
    for c in table.keys():
        table[c] = table[c].transpose().loc[0:8]
        table[c].fillna(0, inplace=True)
        table[c]['Demo Fraction'] = table[c]['demo']/np.sum(table[c], axis=1)
    
    if conditions is None:
        conditions = list(table.keys())
    
    idx = 0
    plot_frame = {}
    for c in conditions:
        for q in table[c].index:
            entry = {}
            entry['Query ID'] = q
            entry['Condition'] = c
            entry['Demo Fraction'] = table[c].loc[q,'Demo Fraction']
            plot_frame[idx] = entry
            idx = idx+1
            
    plot_frame = pd.DataFrame.from_dict(plot_frame, orient = 'index')
    
    palette = create_meta_comparison_palette()
    #conditions = ['Meta Uncertainty','Meta Uncertainty Pedagogical','Meta Info Gain','Meta Info Gain Pedagogical','Meta Model Change','Meta Model Change Pedagogical']
    
    query_strats = ['Meta Uncertainty', 'Meta Info Gain', 'Meta Model Change']
    for q in query_strats:
        conditions = [q, q+' Pedagogical']
        
        filtered_plot_frame = filter_sims(plot_frame, conditions)
        from sns_defaults import rc
        with sns.plotting_context('poster', rc = rc):
            plt.figure(figsize = [10,8])
            sns.barplot(data = filtered_plot_frame, x = 'Query ID', y = 'Demo Fraction', hue = 'Condition', palette = palette, ci = None)
            plt.legend(fontsize=18)
            q_string = q.replace(' ','_')
            savefile = os.path.join(directory, 'ThesisFigs', f'meta_comparison_demo_counts_{q_string}.png')
            plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    #savefile = 
    return plot_frame

def load_meta_noise_data():
    filename = os.path.join(directory, 'meta_noise.pkl')
    with open(filename, 'rb') as file:
        data = dill.load(file)
    data = pad_data(data)
    return data

def create_meta_noise_palette(sims, cmap = 'crest'):
    #sims = create_sims_table(get_similarities(data))
    sels = np.unique(sims['Selectivity'])
    norm = mpl.colors.Normalize(np.min(sels), np.max(sels))
    colormap = plt.cm.ScalarMappable(norm, cmap = cmap)
    colors = {}
    for c in sels:
        colors[c] = colormap.to_rgba(c)
    return colors

def plot_meta_noise_similarity(data = None):
    if data == None:
        data = load_meta_noise_data()
    
    data = get_similarities(data)
    sims = create_sims_table(data)
    
    plot_median_IQR(sims, group_var = 'Selectivity', palette = 'crest', figsize = [24,9])
    # Save the figure
    savefile = os.path.join(directory,'ThesisFigs','meta_noise_similarity.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')

def plot_meta_noise_entropy(data = None):
    if data == None:
        data = load_meta_noise_data()
    
    data = get_entropies(data)
    sims = create_table(data, key = 'Entropy')
    
    plot_median_IQR(sims,  key = 'Entropy', group_var = 'Selectivity', palette = 'crest')
    # Save the figure
    savefile = os.path.join(directory,'ThesisFigs','meta_noise_entropy.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    
def plot_meta_noise_demo_counts(data=None):
    if data == None:
        data = load_meta_noise_data()
    
    sims = create_sims_table(get_similarities(data))
    table = create_key_table(data, key = 'meta_selections')
    
    
    
    for c in table.keys():
        
        if 'demo' not in table[c].index:
            table[c] = table[c].append(pd.Series(name = 'demo'))
        
        table[c] = table[c].transpose().loc[0:8]
        table[c].fillna(0, inplace=True)
        table[c]['Demo Fraction'] = table[c]['demo']/np.sum(table[c], axis=1)
    
    
    conditions = list(table.keys())
    
    
    
    idx = 0
    plot_frame = {}
    for c in conditions:
        for q in table[c].index:
            entry = {}
            entry['Query ID'] = q
            entry['Condition'] = c
            entry['Demo Fraction'] = table[c].loc[q,'Demo Fraction']
            plot_frame[idx] = entry
            idx = idx+1
            
    plot_frame = pd.DataFrame.from_dict(plot_frame, orient = 'index')
    plot_frame['Selectivity'] = [extract_selectivity(c)[1] for c in plot_frame['Condition']]
    fillval = np.max(plot_frame['Selectivity'])+1
    plot_frame['Selectivity'] = plot_frame['Selectivity'].fillna(fillval)
    
    palette = create_meta_noise_palette(sims)
    #conditions = ['Meta Uncertainty','Meta Uncertainty Pedagogical','Meta Info Gain','Meta Info Gain Pedagogical','Meta Model Change','Meta Model Change Pedagogical']
    
    # query_strats = ['Meta Uncertainty', 'Meta Info Gain', 'Meta Model Change']
    # for q in query_strats:
    #     conditions = [q, q+' Pedagogical']
        
    #     filtered_plot_frame = filter_sims(plot_frame, conditions)
    #     from sns_defaults import rc
    cmap = sns.color_palette('crest', as_cmap = True)
    norm = mpl.colors.Normalize(np.min(plot_frame['Selectivity']), np.max(plot_frame['Selectivity']))
    colormap = plt.cm.ScalarMappable(norm, cmap = cmap)
    
    with sns.plotting_context('poster', rc = rc):
        plt.figure(figsize = [10,8])
        sns.barplot(data = plot_frame, x = 'Query ID', y = 'Demo Fraction', hue = 'Selectivity', palette = palette, ci = None)
        plt.legend(fontsize=18)
        ax = plt.gca()
        ax.get_legend().remove()
        cbar = plt.colorbar(colormap, label = 'Selectivity')
        cbar.ax.set_yticks([-4,-2,0,2,4,6])
        cbar.ax.set_yticklabels(['-4','-2','0','2','4','inf'])
        
        
        #q_string = q.replace(' ','_')
    savefile = os.path.join(directory, 'ThesisFigs', f'meta_noise_demo_counts.png')
    plt.savefig(savefile, dpi = 500, bbox_inches = 'tight')
    # #savefile = 
    return plot_frame
    
    
    
    
    


if __name__ == '__main__':

    A=1
    
    
    
    
    
    # directory = f'/home/ajshah/Results/Results_15_Active6'
    # data = read_data(directory)
    # data = pad_data(data)
    
    # plot_frame = create_count_table_disambiguity(data)
    # savefile = os.path.join(directory, 'label_counts.pkl')
    # with open(savefile, 'wb') as file:
    #     dill.dump({'plot_frame': plot_frame}, file)
    
    
    
    
    
#    
#    results = get_similarities(data, format = 'long')
#    plot_similarities_mean(directory, results)
#    plot_similarities_median(directory, results)
#    plot_similarities_box(directory, results)
#    plot_similarities_CI(directory, results)

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

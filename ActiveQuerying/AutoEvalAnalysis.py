#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 17:05:07 2019

@author: ajshah
"""

from Auto_Eval_Active import *
import auto_eval_params as params
import seaborn as sns



def plot_entropy(Entropy):
    plt.figure()
    types = ['Active','Random','Batch', 'Base']
    
    with sns.plotting_context('talk'):
        for t in types:
            sns.kdeplot(Entropy[t], bw = 'scott')
    
        plt.title('Density estimate posterior Entropy')

def plot_similarity(Similarity):
    types = ['Active','Random','Batch', 'Base']
    plt.figure()
    with sns.plotting_context('talk'):
        for t in types:
            sns.distplot(Similarity[t], kde=False, bins = np.linspace(0,1,20), hist_kws = {'histtype':'step', 'lw':3, 'label':t, 'alpha':1})
            #sns.kdeplot(Similarity[t], bw = 'scott')
        plt.legend(loc = 'upper left')
        plt.title('Density estimate of formula similarity')

def plot_bar_plots(all_data):
    #plt.figure()
    with sns.plotting_context('poster'):
        with sns.color_palette('muted'):
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Entropy', hue = 'type')
            sns.barplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'type', estimator = np.mean, capsize = 0.05, ci = 95, alpha = 0.85)
            plt.title('Mean Posterior Entropy')
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper right')
            plt.savefig(os.path.join(params.results_path,'..','Entropy.png'), dpi = 500, bbox_inches = 'tight')
            
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Similarity', hue = 'type')
            sns.barplot(data = all_data, x = 'n_data', y = 'Similarity' , hue = 'type', estimator = np.mean, capsize=0.05, ci = 95, alpha = 0.85)
            plt.title('Median Posterior Similarity')
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper left')
            plt.savefig(os.path.join(params.results_path,'..','Similarity.png'), dpi = 500, bbox_inches = 'tight')
    


 #Change this to change the run for data analysis

if __name__ == '__main__':
    all_data = pd.DataFrame()
    
    for i in [1,2,3,4,5,6]:
        params.n_queries = i
        n = params.n_queries + params.n_demo
        params.results_path = f'/home/ajshah/Results/Results_{n}_with_baseline'
        
        new_data = assimilate_metrics()
        all_data = pd.concat([all_data, new_data])
        all_data.reindex()
        Entropy = report_entropies()
        #plot_entropy(Entropy)
        Similarity = report_similarities()
        #plot_similarity(Similarity)
    plot_bar_plots(all_data)
    

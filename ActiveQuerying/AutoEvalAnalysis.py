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
    with sns.plotting_context('poster', rc = {'axes.labelsize': 28, 'axes.titlesize': 32, 'legend.fontsize': 24, 'xtick.labelsize': 24, 'ytick.labelsize': 22}):
        with sns.color_palette('dark'):
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Entropy', hue = 'type')
            #sns.barplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'type', estimator = np.mean, capsize = 0.05, ci = 95, alpha = 0.85)
            sns.lineplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'Protocol', err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
            plt.title('Mean Entropy', )
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper right')
            plt.savefig(os.path.join(params.results_path,'..','Entropy.png'), dpi = 500, bbox_inches = 'tight')
            
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Similarity', hue = 'type')
            sns.lineplot(data = all_data, x = 'n_data', y = 'Similarity' , hue = 'Protocol', err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)
            #sns.barplot(data = all_data, x = 'n_data', y = 'Similarity' , hue = 'type', estimator = np.median, capsize=0.05, ci = 95, alpha = 0.85)
            plt.title('Median Similarity')
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper left')
            plt.savefig(os.path.join(params.results_path,'..','Similarity.png'), dpi = 500, bbox_inches = 'tight')

def plots(all_data):
    #plt.figure()
    with sns.plotting_context('poster', rc = {'axes.labelsize': 28, 'axes.titlesize': 32, 'legend.fontsize': 24, 'xtick.labelsize': 24, 'ytick.labelsize': 22}):
        with sns.color_palette('dark'):
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Entropy', hue = 'type')
            #sns.barplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'type', estimator = np.mean, capsize = 0.05, ci = 95, alpha = 0.85)
            sns.lineplot(data = all_data, x = 'n_data', y = 'Entropy' , hue = 'Protocol', err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.mean, ci = 95, alpha = 0.85)
            plt.title('Mean Entropy', )
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper right')
            plt.savefig(os.path.join(params.results_path,'..','Entropy.png'), dpi = 500, bbox_inches = 'tight')
            
            plt.figure(figsize=[12,9])
            #sns.boxplot(data = all_data, x = 'n_data', y = 'Similarity', hue = 'type')
            sns.lineplot(data = all_data, x = 'n_data', y = 'Similarity' , hue = 'Protocol', err_style = 'bars', err_kws = {'capsize':10, 'capthick':3}, estimator = np.median, ci = 95, alpha = 0.85)
            #sns.barplot(data = all_data, x = 'n_data', y = 'Similarity' , hue = 'type', estimator = np.median, capsize=0.05, ci = 95, alpha = 0.85)
            plt.title('Median Similarity')
            plt.xlabel('Number of task executions')
            plt.legend(loc='upper left')
            plt.savefig(os.path.join(params.results_path,'..','Similarity.png'), dpi = 500, bbox_inches = 'tight')

def bar_plots(all_data):
    #plt.figure()
    with sns.plotting_context('poster', rc = {'axes.labelsize': 28, 'axes.titlesize': 32, 'legend.fontsize': 24, 'xtick.labelsize': 24, 'ytick.labelsize': 22}):
        with sns.color_palette('muted'):
            plt.figure(figsize=[12,9])
            sns.barplot(data = all_data, x = 'Protocol', y = 'Entropy', hue = 'Type', capsize = 0.05, ci = 95, alpha = 1)
            plt.title('Mean Entropy', )
            plt.xlabel('Number of task executions')
            #plt.legend(loc='upper right')
            plt.savefig(os.path.join(params.results_path,'..','SimTable_Entropy.png'), dpi = 500, bbox_inches = 'tight')
            
            plt.figure(figsize=[12,9])
            sns.barplot(data = all_data, x = 'Protocol', y = 'Similarity', hue='Type' , capsize=0.05, ci = 95, alpha = 1, estimator = np.mean)
            plt.ylim(top = 1.25)
            #plt.title('Mean Similarity')
            #plt.xlabel('Number of task executions')
            plt.legend(loc='lower left')
            plt.savefig(os.path.join(params.results_path,'..','SimTable_Similarity.png'), dpi = 500, bbox_inches = 'tight')


 #Change this to change the run for data analysis

if __name__ == '__main__':
    all_data = pd.DataFrame()
    
    for i in [3]:
        params.n_queries = i
        n = params.n_queries + params.n_demo
        params.results_path = f'/home/ajshah/Results/TableSetup_{n}_with_baseline'
        
        new_data = assimilate_metrics(['Active','Random','Batch'])
        all_data = pd.concat([all_data, new_data])
        all_data.reindex()
        Entropy = report_entropies(['Active','Random','Batch'])
        #plot_entropy(Entropy)
        Similarity = report_similarities(['Active','Random','Batch'])
        #plot_similarity(Similarity)
    all_data['Protocol'] = all_data['type']
    bar_plots(all_data)
    

from AutoEvalAnalysis import *
from puns.utils import CreateSmallDinnerMDP
from puns.ControlMDP import SmallTableMDP
from puns.SpecificationMDP import *
import json
import os
from scipy.stats import entropy
import pandas as pd
import pingouin as pg

results_path = '/home/ajshah/Results/TableSetup_Task2_5_with_baseline'

true_formula = ['and']
true_formula.append(Globally('W0'))
true_formula.append(Globally('W2'))
true_formula.append(Eventually('W1'))
true_formula.append(Eventually('W3'))
true_formula.append(Eventually('W4'))

def collect(data, label='Experiment'):
    final_data = {}
    i = 0

    for row in data.iterrows():
            final_data[i] = {}
            final_data[i]['Similarity'] = row[1]['Similarity']
            final_data[i]['Entropy'] = row[1]['Entropy']
            final_data[i]['Protocol'] = row[1]['Protocol']
            final_data[i]['Type'] = label
            i=i+1
    return pd.DataFrame.from_dict(final_data, orient = 'index')


if __name__ == '__main__':

    params.n_queries = 3
    params.results_path = results_path

    sim_data = assimilate_metrics(['Active','Random','Batch'])
    Entropy = report_entropies(['Active','Random','Batch'])
    Similarity = report_similarities(['Active','Random','Batch'])
    sim_data['Protocol'] = sim_data['type']
    new_data = collect(sim_data, 'Simulated')

    bar_plots(new_data)

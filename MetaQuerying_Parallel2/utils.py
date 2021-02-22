from numpy.random import binomial
from puns.utils import CreateSpecMDP, Eventually, Order, Globally
import matplotlib.pyplot as plt
import networkx as nx
import params.auto_eval_params as global_params
import os

def sample_subset(values, p = 0.5):
    subset = []
    for val in values:
        if binomial(1,p):
            subset.append(val)
    return subset

def divide_into_subsets(values, p = 0.5):
    subsets = []

    for val in values:
        if len(subsets)==0:
            sub = [val]
            subsets.append(sub)
        else:
            if binomial(1,p): #divide
                sub = [val]
                subsets.append(sub)
            else:
                subsets[-1].append(val)

    return subsets

def create_orders(subsets):
    orders = []
    for subset in subsets:
        for (i,val) in enumerate(subset):
            new_orders = [(val, child) for child in subset[i+1::]]
            orders.extend(new_orders)
    return orders


def sample_ground_truth(n_waypoints = 5, threats = False):

    values = [f'W{i}' for i in range(n_waypoints)]
    waypoints = sample_subset(values)
    orders = create_orders(divide_into_subsets(values))
    order_waypoints = [o[0] for o in orders]
    waypoints = list(set(waypoints) | set(order_waypoints))

    if threats:
        threat_candidates = list(set(values) - set(waypoints))
        if len(threat_candidates) > 0:
            threats = sample_subset(threat_candidates)
        else:
            threats = []
    else:
        threats = []

    if len(waypoints) == 0 and len(orders)==0 and len(threats) == 0:
        ground_truth_formula = [True]
    elif len(waypoints)+len(orders)+len(threats) == 1:
        ground_truth_formula = []
        for threat in threats:
            ground_truth_formula.append(Globally(threat))
        for waypoint in waypoints:
            ground_truth_formula.append(Eventually(waypoint))
        for order in orders:
            ground_truth_formula.append(Order(*order))

        ground_truth_formula = ground_truth_formula[0]
    else:
        ground_truth_formula = ['and']
        for threat in threats:
            ground_truth_formula.append(Globally(threat))
        for waypoint in waypoints:
            ground_truth_formula.append(Eventually(waypoint))
        for order in orders:
            ground_truth_formula.append(Order(*order))


    return ground_truth_formula

def clear_demonstrations(directory, params):
    files = os.listdir(os.path.join(directory, params.compressed_data_path))
    for f in files:
        os.remove(os.path.join(directory, params.compressed_data_path, f))

def label_slice(trace_slice):
    label = 'S'
    for key in trace_slice.keys():
        if trace_slice[key]: label = key
    return label

def visualize_query(trace, query_number=1):
    labels = {}
    G = nx.DiGraph()

    for (i,slice) in enumerate(trace):
        G.add_node(i)
        if i>0: G.add_edge(i-1, i)
        labels[i] = label_slice(slice)


    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw_networkx(G,pos, with_labels = False)
    _ = nx.draw_networkx_labels(G,pos, labels, font_color='w')
    plt.title(f'Query {query_number}')
    plt.box=False

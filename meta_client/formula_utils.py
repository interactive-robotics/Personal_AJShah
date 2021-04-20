#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 18:47:46 2020

@author: ajshah
"""

import numpy as np

def waypoints_and_orders(formula):
    #assume that formula is in ['and',....] format
    waypoints = []
    orders = []
    threats = []

    if formula[0] == 'and':
        subformulas = formula[1::]
    else:
        subformulas = [formula]

    for sub_formula in subformulas:
        if sub_formula[0] == 'F':
            waypoints.append(sub_formula[1][0])
        elif sub_formula[0]=='U':
            w1 = sub_formula[2][0]
            w2 = sub_formula[1][1][0]
            orders.append((w1,w2))
            waypoints.append(w1)
        elif sub_formula[0] == 'G':
            threats.append('G' + sub_formula[1][1][0])
        else:
            waypoints.append(0)

        #Remove the orders whose precedents are in Globals

        for order in orders:
            if 'G' + order[1] in threats:
                orders.remove(order)

    return waypoints, orders, threats

def compare_formulas(formula_1, formula_2):

    # Assume that they are in ['and' ...] format
    waypoints1, orders1, globals1 = waypoints_and_orders(formula_1)
    waypoints2, orders2, globals2 = waypoints_and_orders(formula_2)

    clauses_1 = set(waypoints1 + orders1 + globals1)
    clauses_2 = set(waypoints2 + orders2 + globals2)
    try:
        L = len(set.intersection(clauses_1,clauses_2))/len(set.union(clauses_1,clauses_2))
    except:
           print(clauses_1, clauses_2)
           print(formula_1, formula_2)
           L = 0
    return L

def compare_distribution(true_formula, distribution):
    similarities = [compare_formulas(true_formula, form) for form in distribution['formulas']]
    return np.dot(similarities, distribution['probs'])

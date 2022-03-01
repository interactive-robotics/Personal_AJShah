# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 13:07:11 2022

@author: AJShah
"""

import numpy as np
from ltlf2ltl_translator import *
import sys
try:
    import spot
except:
    print('Spot not installed')


global_props = ['thayer', 'waterman']
locations = {}
locations['thayer'] = ['store','cafe']
locations['waterman'] = ['bank']

def sample_formula(spot_str = True):
    
    clauses = []
    
    #First determine global proposition
    
    #Flip coin to see if there is global proposition
    global_clause, global_flip, stay_flip = sample_global_clauses()
    #print('Global clause: ', global_clause)
    
    #Determine visitable locations
    feasible_locations = determine_feasible_locations(global_clause, stay_flip, global_flip)
    
    #determine locations to be visited
    visit_locations = determine_visit_locations(feasible_locations)
    #print('visit_locations: ', visit_locations)
    visit_clauses = [['F',[clause]] for clause in visit_locations]
    
    #determine relative ordering of locations to be visited
    #Using set of linear chains formalism
    linear_chains = determine_orders(visit_locations)
    
    
    #Convert Linear chains into LTL constraints
    order_clauses = order2constraints(linear_chains) 
    
    #Compile the tree LTL formula
    if len(global_clause) > 0:
        clauses.append(global_clause)
    
    clauses.extend(visit_clauses)
    clauses.extend(order_clauses)
    
    if len(clauses) == 0:
        formula =  True
    elif len(clauses) == 1:
        formula = clauses[0]
    else:
        formula = ['and']
        formula.extend(clauses)
    
    #check if output required in spot string or tree format
    if spot_str:
        if formula==True:
            return True
        else:
            return ltl_tree2string(formula)
    else:
        return formula


def ltl2digraph(formula):
    if 'spot' not in sys.modules:
        print('Spot not installed/imported')
        return
    
    nodelist = defaultdict(dict)
    bdd = aut.get_dict()

    for state in range(aut.num_states()):
        for edge in aut.out(state):
            edge_formula = spot.bdd_format_formula(bdd, edge.cond)
            out_state = edge.dst
            nodelist[state][out_state] = edge_formula
    return nodelist


def sample_global_clauses():
    global_flip = np.random.binomial(1,0.5)
    if global_flip:
        
        #Determine stay or avoid
        stay_flip = np.random.binomial(1,0.5)
        global_prop = np.random.choice(global_props)
        
        global_subformula = [global_prop] if stay_flip else ['not',[global_prop]]
        global_clause = ['G',global_subformula]
        return global_clause, global_flip, stay_flip
    else:
        return [], global_flip, False

def determine_feasible_locations(global_clause, stay_flip, global_flip):
    feasible_locations = []
    if global_flip:
        #return only locations on the street if stay flip
        if stay_flip:
            feasible_locations = locations[global_clause[1][0]]
        else: #return all locations not on the avoidance street
            #feasible_locations = []
            streets = [key for key in locations if key != global_clause[1][1][0]]
            for key in streets:
                for loc in locations[key]:
                    feasible_locations.append(loc)
    else:
        #return all locations
        for key in locations:
            for loc in locations[key]:
                feasible_locations.append(loc)
    return feasible_locations

def determine_visit_locations(feasible_locations):
    #flip a coin for each location
    visit_locations = [loc for loc in feasible_locations if np.random.binomial(1,0.5)]
    return visit_locations

def determine_orders(visit_locations):
    
    linear_chains = []
    if len(visit_locations) == 0:
        return []
    
    visit_locations = np.random.permutation(visit_locations)
    
    new_chain = [visit_locations[0]]
    
    for loc in visit_locations[1::]:
        #either add to existing chain or start a new chain
        if np.random.binomial(1,0.5):
            new_chain.append(loc)
        else:
            linear_chains.append(new_chain)
            new_chain = [loc]
    linear_chains.append(new_chain)
    return linear_chains

def lc2binary_orders(lc):
    binary_orders = []
    for (i,loc) in enumerate(lc):
        for loc2 in lc[i+1::]:
            binary_orders.append([loc,loc2])
    return binary_orders

def nest_eventuals(lc):
    if len(lc) == 1:
        return ['F',[lc[0]]]
    else:
        return ['F',['and',[lc[0]],nest_eventuals(lc[1::])]]
        
def order2constraints(linear_chains):
    clauses = []
    if len(linear_chains) > 0:
        for lc in linear_chains:
            if len(lc) == 1:
                continue
            else:
                #Sample soft ordering or binary ordering
                soft = np.random.binomial(1,0.5)
                if soft: #This linear chain will use nested eventuals to sequence
                    clauses.append(nest_eventuals(lc))
                else: #Binarize the orders and sample hard constraint or soft order individually
                    orders = lc2binary_orders(lc)
                    for order in orders:
                        soft = np.random.binomial(1,0.5)
                        if soft:
                            clauses.append(['F',['and',[order[0]],['F',[order[1]]]]])
                        else:
                            clauses.append(['U',['not',[order[1]]],[order[0]]])
        return clauses
    else:
        return []

                    
            
    
    
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:53:40 2019

@author: ajshah
"""

import sys
sys.path.append('/home/ajshah/Github/Project_LMMIT/Phase2Models')
from CreatePropositions import *
import os,json

Operators = set(['and','or','imp','not','X','U','wU','R','G','F'])
Literals = set(['true','false',True, False])

SampleDataPath = '/home/ajshah/Github/SpecificationInference/Project_LMMIT/SpecificationInference/'


BinaryOperators = set(['and','or','imp','U','wU','R'])
UnaryOperators = set(['not','X','F','G'])

def ImportSampleData(PathToData, i=10):
    
    RawDataFile = os.path.join(PathToData,f'Predicates_{i}.json')
    RawData = json.load(open(RawDataFile,'r'))
    
    Signal = {}
    
    for i in range(len(RawData['WaypointPredicates'])):
        Signal[f'W{i}'] = RawData['WaypointPredicates'][i]
    
    for i in range(len(RawData['ThreatPredicates'])):
        Signal[f'T{i}'] = [val for val in RawData['ThreatPredicates'][i]]
    
    for i in range(len(RawData['PositionPredicates'])):
        Signal[f'P{i}'] = [not val for val in RawData['PositionPredicates'][i]]
    
    Signal['length'] = len(list(Signal.values())[0])
    return Signal


def ImportCandidateFormulas():
    
    ResultsFile = 'ThreatData_OutputDist_Sampler5_Custom_5.json'
    Data = json.load(open(ResultsFile,'r'))
    Formulas = Data['support']
    Probs = Data['probs']
    return Formulas, Probs

def ImportBSIData(path):
    RawData = json.load(open(path,'r'))
    Signal = {}
    
    for i in range(len(RawData['WaypointPredicates'])):
        Signal[f'W{i}'] = RawData['WaypointPredicates'][i]
    
    for i in range(len(RawData['ThreatPredicates'])):
        Signal[f'T{i}'] = RawData['ThreatPredicates'][i]
        
    for i in range(len(RawData['PositionPredicates'])):
        Signal[f'P{i}'] = [not val for val in RawData['PositionPredicates'][i]]
    
    Signal['length'] = len(list(Signal.values())[0])
    return Signal
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:53:40 2019

@author: ajshah
"""


import Constants
from FormulaTools import *
from ProgressOperators import *
import numpy.random as random
import numpy as np



def Progress(formula, Signal, t=None):
    
    if t==None:
        t = Signal['length'] #By Default progress the sequence through the entire trace
    #First verify that the signal and formula vocabulary match
    if GetVocabulary(formula, set()).issubset(set(Signal.keys())|set([True, False])-set(['length'])): #Vocab check
        
        for i in range(t-1): #Progress till the penultimate time step
            SignalSlice = GetTraceSlice(Signal, i)
            formula = ProgressSingleTimeStep(formula,SignalSlice)
        
        if t<Signal['length']:
            SignalSlice = GetTraceSlice(Signal,t-1)
            formula = ProgressSingleTimeStep(formula, SignalSlice)
        else:
            SignalSlice = GetTraceSlice(Signal,t-1)
            formula = ProgressSingleTimeStep(formula, SignalSlice, final=True)
        return formula
        
    else:
        raise Exception('Formula and signal vocabulary mismatch')



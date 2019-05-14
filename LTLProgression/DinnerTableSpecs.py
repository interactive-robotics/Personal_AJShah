#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 15:01:56 2019

@author: ajshah
"""

import json
import numpy as np

if __name__ == '__main__':
    
    with open('DinnerTable_OutputDist_Sampler4_Custom_30.json','r') as file:
        Data = json.load(file)
        support = Data['support']
        probs = Data['probs']
        
        idx = np.argsort(probs)[::-1]
        probs = np.array(probs)[idx]
        formulas = [support[i] for i in idx]
        
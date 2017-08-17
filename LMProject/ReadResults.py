#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 20:01:07 2017

@author: ajshah
"""

import pickle
import numpy as np

FeatureClass = 'OwnshipData'
#filename = 'RNNResults_'+FeatureClass+'.pkl'
filename = 'NNResults.pkl'

Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4C']

with open(filename,'rb') as file:
    data = pickle.load(file)

TestAcc = np.array(data['TestAccuracies'])

meanAcc = np.mean(TestAcc)
maxAcc = np.max(TestAcc)
minAcc = np.min(TestAcc)

ScenMax = Scenarios[np.argmax(TestAcc)]
ScenMin = Scenarios[np.argmin(TestAcc)]

results = np.array(list(zip(Scenarios,data['TestAccuracies'])))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 16:39:01 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from sklearn.svm import SVC,LinearSVC
from PrepareFeatures import *
import pickle

#Prepare the data

def TrainLinearSVC(scenarios, TestScenario, FeatureClass, WindowSize=5):
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    
    if FeatureClass == 'OwnshipData':
        GetData = GetTestAndTrainDataOwnship
    elif FeatureClass == 'OwnshipWingmanData':
        GetData = GetTestAndTrainDataOwnshipWingman

    [X_train, y_train, X_test, y_test] = GetData(TrainScenarios, TestScenario, WindowSize = WindowSize)
    
    model = LinearSVC(verbose = True)
    model.fit(X_train, y_train)
    predLabels_train = model.predict(X_train)
    TrainAcc = np.mean(predLabels_train == y_train)
    
    predLabels_test = model.predict(X_test)
    TestAcc = np.mean(predLabels_test == y_test)
    
    return model, TrainAcc, TestAcc, predLabels_test

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5):
    models = {}
    TestAccs = []
    predLabels_test = {}

    for TestScenario in TestScenarios:
        
        new_model,new_TrainAcc,new_TestAcc,new_predLabels_test = TrainLinearSVC(Scenarios, [TestScenario], FeatureClass, WindowSize)
        models[TestScenario] = new_model
        TestAccs.append(new_TestAcc)
        predLabels_test[TestScenario] = new_predLabels_test
        
    return models, TestAccs, predLabels_test

if __name__=='__main__':
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenario = ['1C']
#    model, TestAcc, predLabels_test = TrainLinearSVC(Scenarios, TestScenario, 'OwnshipWingmanData')


    # Test LOOCV
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','2A']
    models, TestAccs, predLabels_test = LOOCV(Scenarios, TestScenarios, 'OwnshipWingmanData')
    with open('LinearSVCResults_'+FeatureClass+'_'+'.pkl','wb') as file:
        pickle.dump({'Models':models, 'TestAccuracies':TestAccs, 'PredictedTestLabels':predLabels_test},file)
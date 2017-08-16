#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 20:13:08 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from sklearn.svm import SVC,LinearSVC
from sklearn.ensemble import RandomForestClassifier
from PrepareFeatures import *
import pickle

def TrainKernelSVC(scenarios, TestScenario, FeatureClass, WindowSize=5):
    
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    
    if FeatureClass == 'OwnshipData':
        GetData = GetTestAndTrainDataOwnship
    elif FeatureClass == 'OwnshipWingmanData':
        GetData = GetTestAndTrainDataOwnshipWingman

    [X_train, y_train, X_test, y_test] = GetData(TrainScenarios, TestScenario, WindowSize = WindowSize)
    
    
    model = SVC(kernel = 'rbf', decision_function_shape = 'ovr', verbose = True, max_iter = 1000)
    model.fit(X_train, y_train)
    pred_train_labels = model.predict(X_train)
    TrainAcc = np.mean(pred_train_labels == y_train)

    pred_test_labels = model.predict(X_test)
    TestAcc = np.mean(pred_test_labels == y_test)
    
    return model, TrainAcc, TestAcc, pred_test_labels

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5):
    models = {}
    TestAccs = []
    predLabels_test = {}

    for TestScenario in TestScenarios:
        
        new_model,new_TrainAcc,new_TestAcc,new_predLabels_test = TrainKernelSVC(Scenarios, [TestScenario], FeatureClass, WindowSize)
        models[TestScenario] = new_model
        TestAccs.append(new_TestAcc)
        predLabels_test[TestScenario] = new_predLabels_test
        
    return models, TestAccs, predLabels_test
#%%

if __name__=='__main__':
    
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenario = ['4A']
#    model, TrainAcc, TestAcc, pred_test_labels = TrainKernelSVC(Scenarios, TestScenario, 'OwnshipData')
    
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','2A']
    FeatureClass = 'OwnshipWingmanData'
    models, TestAccs, predLabels_test = LOOCV(Scenarios, TestScenarios, FeatureClass=FeatureClass)
    with open('KernelSVCResults_'+FeatureClass+'_'+'.pkl','wb') as file:
        pickle.dump({'Models':models, 'TestAccuracies':TestAccs, 'PredictedTestLabels':predLabels_test},file)
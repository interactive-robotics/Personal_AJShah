#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 20:13:08 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from sklearn.svm import SVC,LinearSVC
from PrepareFeatures import *
import pickle
import os

def CreateFeatureClass(WingmanData=True, FlightPlanData=True, WeaponsData=True, CommsData=True):
    
    FeatureClass = {}
    FeatureClass['WingmanData'] = WingmanData
    FeatureClass['FlightPlanData'] = FlightPlanData
    FeatureClass['WeaponsData'] = WeaponsData
    FeatureClass['CommsData'] = CommsData
    
    return FeatureClass

def GetData(scenarios, TestScenario, FeatureClass, WindowSize=5):
    
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    WingmanData = FeatureClass['WingmanData']
    FlightPlanData = FeatureClass['FlightPlanData']
    WeaponsData = FeatureClass['WeaponsData']
    CommsData = FeatureClass['CommsData']
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GenerateWindowedTestAndTrainData(TrainScenarios, TestScenario, WindowSize=WindowSize,
                                                                    WingmanData=WingmanData, FlightPlanData = FlightPlanData,
                                                                    WeaponsData=WeaponsData, CommsData=CommsData)
    
    YTrain = np.array(YTrain).ravel()
    YTest = np.array(YTest).ravel()
    return XTrain, YTrain, XTest, YTest, Offsets, Scale

def TrainKernelSVC(XTrain, YTrain):

    model = SVC(kernel = 'rbf', decision_function_shape = 'ovr', verbose = True, max_iter = 1000)
    
    model.fit(XTrain, YTrain)
    pred_train_labels = model.predict(XTrain)
    TrainAcc = np.mean(pred_train_labels == np.array(YTrain))

    return model, TrainAcc

def TrainAndEvalKernelSVC(Scenarios, TestScenario, FeatureClass, WindowSize=5):
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GetData(Scenarios, TestScenario, FeatureClass, WindowSize=WindowSize)
    
    model, TrainAcc = TrainKernelSVC(XTrain, YTrain)
    PredLabels = model.predict(XTest)
    TestAcc = np.mean(PredLabels == YTest)
    
    return model, TrainAcc, TestAcc, PredLabels, Offsets, Scale

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SaveResult=False, filename = 'KernelSVCResults'):

    #ensure the filename is unique to prevent writeover
    # Assumes that the filename ends in .pkl
    i=1
    if os.path.exists(filename+'.pkl'):
        filenameNew = filename+'_'+str(i)
        while os.path.exists(filenameNew+'.pkl'):
            i=i+1
            filenameNew = filename+'_'+str(i)
    else:
        filenameNew = filename

    filenameNew = filenameNew+'.pkl'
    
    Models = {}
    TestAccs = {}
    PredLabelsTest = {}
    TrainAccs = {}
    
    for TestScenario in TestScenarios:
        
        model, TrainAcc, TestAcc, PredLabels, Offsets, Scale = TrainAndEvalKernelSVC(Scenarios, [TestScenario], FeatureClass, WindowSize=WindowSize)
        Models[TestScenario] = model
        TestAccs[TestScenario] = TestAcc
        TrainAccs[TestScenario] = TrainAcc
        PredLabelsTest[TestScenario] = PredLabels
        
        
    if SaveResult == True:
        OutData = dict()
        OutData['TestAccuracies'] = TestAccs
        OutData['Models'] = Models
        OutData['PredictedTestLabels'] = PredLabelsTest
        OutData['TrainingAccuracies'] = TrainAccs
        OutData['FeatureClass'] = FeatureClass
        OutData['WindowSize'] = WindowSize
        with open(filenameNew,'wb') as file:
            pickle.dump(OutData,file)

    return OutData
#%%

if __name__=='__main__':
    
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenario = ['4A']
#    model, TrainAcc, TestAcc, pred_test_labels = TrainKernelSVC(Scenarios, TestScenario, 'OwnshipData')
    
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['2A']
    FeatureClass = CreateFeatureClass(WingmanData=False)
    #model, TrainAcc, TestAcc, PredLabels, Offsets, Scale = TrainAndEvalKernelSVC(Scenarios, TestScenarios, FeatureClass, WindowSize=5)
    
    filename =LOOCV(Scenarios, TestScenarios, FeatureClass=FeatureClass, SaveResult=True)

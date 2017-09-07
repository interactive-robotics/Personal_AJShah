#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 16:39:01 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from PrepareFeatures import *
import pickle
import os

#Prepare the data

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



def TrainLR(XTrain, YTrain):

    model = LogisticRegression(solver = 'lbfgs',verbose=1)
    
    model.fit(XTrain, YTrain)
    pred_train_labels = model.predict(XTrain)
    TrainAcc = np.mean(pred_train_labels == np.array(YTrain))

    return model, TrainAcc



def TrainAndEvalLR(Scenarios, TestScenario, FeatureClass, WindowSize=5):
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GetData(Scenarios, TestScenario, FeatureClass, WindowSize=WindowSize)
    
    model, TrainAcc = TrainLR(XTrain, YTrain)
    PredLabels = model.predict(XTest)
    TestAcc = np.mean(PredLabels == YTest)
    
    return model, TrainAcc, TestAcc, PredLabels, Offsets, Scale



def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SaveResult=False, filename = 'LRResults'):

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
        
        model, TrainAcc, TestAcc, PredLabels, Offsets, Scale = TrainAndEvalLR(Scenarios, [TestScenario], FeatureClass, WindowSize=WindowSize)
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
        with open(filenameNew,'wb') as file:
            pickle.dump(OutData,file)

    return OutData


if __name__=='__main__':
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenario = ['1C']
#    model, TestAcc, predLabels_test = TrainLinearSVC(Scenarios, TestScenario, 'OwnshipWingmanData')


    # Test LOOCV
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['1A','2A']
    #TestScenarios = ['1A','2A']
    FeatureClass = CreateFeatureClass(WingmanData=False)
    OutData = LOOCV(Scenarios, TestScenarios, FeatureClass, SaveResult=True, WindowSize=5)
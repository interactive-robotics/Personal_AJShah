
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 20:01:06 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from sklearn.svm import SVC,LinearSVC
from sklearn.ensemble import RandomForestClassifier
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



def TrainRandomForests(XTrain, YTrain):

    model = RandomForestClassifier(n_estimators = 5, min_samples_split = 50, min_samples_leaf = 20, verbose = True)
    
    model.fit(XTrain, YTrain)
    pred_train_labels = model.predict(XTrain)
    TrainAcc = np.mean(pred_train_labels == np.array(YTrain))

    return model, TrainAcc



def TrainAndEvalRandomForests(Scenarios, TestScenario, FeatureClass, WindowSize=5):
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GetData(Scenarios, TestScenario, FeatureClass, WindowSize=WindowSize)
    
    model, TrainAcc = TrainRandomForests(XTrain, YTrain)
    PredLabels = model.predict(XTest)
    TestAcc = np.mean(PredLabels == YTest)
    
    return model, TrainAcc, TestAcc, PredLabels, Offsets, Scale



def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SaveResult=False, filename = 'RandomForestsResults'):

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
        
        model, TrainAcc, TestAcc, PredLabels, Offsets, Scale = TrainAndEvalRandomForests(Scenarios, [TestScenario], FeatureClass, WindowSize=WindowSize)
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
#    TestScenario = ['2A']
#    model, TrainAcc, TestAcc, pred_test_labels = TrainRandomForests(Scenarios, TestScenario, 'OwnshipData')
    
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['1A']
    FeatureClass = CreateFeatureClass(WingmanData=False)
    OutData = LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SaveResult=True)

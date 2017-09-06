#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 19:42:23 2017

@author: ajshah
"""

import numpy as np
import pandas as pd
from PrepareFeaturesRNN import *
from PrepareFeatures import *

scenarios = ['1A','1B','1C', '2A','2B','2C', '3A','3B','3C', '4A','4C']
TestScenario = ['4C']

path = '/home/ajshah/Dropbox (MIT)/Data'

def PrepareRNNData(scenarios, TestScenario, WindowSize=5, SeqSize = 100,
                   OwnshipData=True, WingmanData=False, FlightPlanData=True,
                   WeaponsData=True, CommsData=True):
    
    [X_train, y_train, X_test, y_test, TrainStartID, TrainEndID, TestStartID,
    TestEndID] = GenerateWindowedTestAndTrainData(
                                                scenarios, TestScenario,
                                                WindowSize=WindowSize,
                                                OwnshipData=OwnshipData,
                                                WingmanData=WingmanData,
                                                FlightPlanData = FlightPlanData,
                                                WeaponsData = WeaponsData,
                                                CommsData=CommsData,
                                                RNNMode=True)
    
    SeqX_train, SeqY_train, SeqX_test, SeqY_test = PrepareSequenceData(
            X_train, y_train, X_test, y_test, TrainStartID, TrainEndID,
            TestStartID, TestEndID, WindowSize=WindowSize, SeqSize=SeqSize)
    
    return SeqX_train, SeqY_train, SeqX_test, SeqY_test


def PrepareSequenceData(X_train, y_train, X_test, y_test, TrainStartID,
                        TrainEndID, TestStartID, TestEndID, WindowSize=5,
                        SeqSize=100):
    
    y_test = np.array(pd.get_dummies(y_test))
    y_train = np.array(pd.get_dummies(y_train))
    
    SeqX_train = np.zeros((0,SeqSize, X_train.shape[1]))
    SeqY_train = np.zeros((0,SeqSize, y_train.shape[1]))
    
    for i in range(len(TrainStartID)):
    #for i in [1]:
        ScenarioData = X_train[TrainStartID[i]:TrainEndID[i],:]
        ScenarioLabels = y_train[TrainStartID[i]:TrainEndID[i],:]
        dataChops = np.arange(0, ScenarioData.shape[0], SeqSize)
        for j in range(len(dataChops)-1):
            newSeqData = ScenarioData[dataChops[j]:dataChops[j+1],:]
            newSeqData = np.reshape(newSeqData,(1,*newSeqData.shape))
            SeqX_train = np.append(SeqX_train, newSeqData, axis=0)
            
            newLabels = y_train[dataChops[j]:dataChops[j+1],:]
            newLabels = np.reshape(newLabels,(1,*newLabels.shape))
            SeqY_train = np.append(SeqY_train, newLabels,axis=0)
        
        LastData = ScenarioData[dataChops[-1]:,:]
        LastSeqData = np.zeros((1,SeqSize,X_train.shape[1]))
        LastSeqData[0,0:LastData.shape[0],:] = LastData
        SeqX_train = np.append(SeqX_train,LastSeqData, axis=0)
        
        LastLabels = ScenarioLabels[dataChops[-1],:]
        LastSeqLabels = np.zeros((1,SeqSize,y_train.shape[1]))
        LastSeqLabels[0,0:LastLabels.shape[0],:] = LastLabels
        SeqY_train = np.append(SeqY_train,LastSeqLabels,axis=0)
    
    
    SeqX_test = np.zeros((0,SeqSize,X_test.shape[1]))
    SeqY_test = np.zeros((0,SeqSize,y_test.shape[1]))
    
    for i in range(len(TestStartID)):
    #for i in [1]:
        ScenarioData = X_test[TestStartID[i]:TestEndID[i],:]
        ScenarioLabels = y_test[TestStartID[i]:TestEndID[i],:]
        dataChops = np.arange(0, ScenarioData.shape[0], SeqSize)
        for j in range(len(dataChops)-1):
            newSeqData = ScenarioData[dataChops[j]:dataChops[j+1],:]
            newSeqData = np.reshape(newSeqData,(1,*newSeqData.shape))
            SeqX_test = np.append(SeqX_test, newSeqData, axis=0)
            
            newLabels = y_test[dataChops[j]:dataChops[j+1],:]
            newLabels = np.reshape(newLabels,(1,*newLabels.shape))
            SeqY_test = np.append(SeqY_test, newLabels,axis=0)
        
        LastData = ScenarioData[dataChops[-1]:,:]
        LastSeqData = np.zeros((1,SeqSize,X_train.shape[1]))
        LastSeqData[0,0:LastData.shape[0],:] = LastData
        SeqX_test = np.append(SeqX_test,LastSeqData, axis=0)
        
        LastLabels = ScenarioLabels[dataChops[-1],:]
        LastSeqLabels = np.zeros((1,SeqSize,y_train.shape[1]))
        LastSeqLabels[0,0:LastLabels.shape[0],:] = LastLabels
        SeqY_test = np.append(SeqY_test,LastSeqLabels,axis=0)
        
        
    return SeqX_train, SeqY_train, SeqX_test, SeqY_test

if __name__ == '__main__':
    scenarios = ['1A','1B','1C', '2A','2B','2C', '3A','3B','3C', '4A','4C']
    TestScenario = ['4C']
    #SeqX_train, SeqY_train, SeqX_test, SeqY_test = ReadRNNData(scenarios, TestScenario, 'OwnshipData')
    XTrain, YTrain, XTest, YTest = PrepareRNNData(scenarios, TestScenario,
                                                  WindowSize=5, SeqSize=50,
                                                  WingmanData=False,
                                                  FlightPlanData = False,
                                                  WeaponsData=False,
                                                  CommsData=False)
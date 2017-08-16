#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 17:31:13 2017

@author: ajshah
"""

import pandas as pd
import numpy as np

#Return the features as a windowed numpy array (post conversion)

#scenarios = ['1A', '1B', '1C']
#FeatureClass = 'OwnshipData'
#players = ['Cool21', 'Cool22']
#
#Features = pd.DataFrame()
#StartID = []
#EndID = []
#Labels = pd.DataFrame()

def GetFeatures(scenarios, FeatureClass):
    
    #define data path here
    path = '/home/ajshah/Dropbox (MIT)/Data'
    
    
    Features = pd.DataFrame()
    StartID = []
    EndID = []
    Labels = pd.DataFrame()

    for scenario in scenarios:
        if scenario == '1A':
            players = ['Cool22']  #Discarding data to Cool21 in 1A
        else:
            players = ['Cool21','Cool22']
        for player in players:
            
            filename = FeatureClass+'/'+scenario+'_'+player+'.pkl'
            data = pd.read_pickle(filename)
            
            NewFeatures = data.ix[:,data.columns!='Label']
            NewFeatures = NewFeatures.ix[:,NewFeatures.columns!='Time']
            if scenario == '4C' and player == 'Cool21':
                NewFeatures = NewFeatures.iloc[17:,:]
            StartID.append(Features.shape[0])
            Features = pd.concat([Features,NewFeatures])
            EndID.append(Features.shape[0])
            
            Labels = pd.concat([Labels, data['Label']])
    
    Labels = Labels.iloc[:,0].astype('category')
    #Features['NextWPIndex'] = Features['NextWPIndex'].astype('category')
    Features['NextWPIndex'] = pd.Categorical(Features['NextWPIndex'] , categories = [0,1,2,3,4,5,6,7,8,9,10])
    NumericFeatures = pd.np.array(pd.get_dummies(Features))
    return NumericFeatures, Labels, StartID, EndID
def CreateWindowFeatures(NumericFeatures, Labels, StartID, EndID, WindowSize):
    #WindowSize = 4
    WindowFeatures = pd.np.zeros([0,WindowSize*NumericFeatures.shape[1]])
    Labels_final = pd.DataFrame()
    
    for i in range(len(StartID)):
        WindowFeatures_scenario = pd.np.zeros([EndID[i] - WindowSize - StartID[i],WindowFeatures.shape[1]])
        Labels_scenario = pd.DataFrame()
        for (index,j) in enumerate(range(StartID[i], EndID[i]-WindowSize)):
            FeatureSet = NumericFeatures[j:j+WindowSize,:]
            FlatFeatureSet = FeatureSet.flatten()
            WindowFeatures_scenario[index] = FlatFeatureSet
            Labels_scenario = pd.concat([Labels_scenario, pd.DataFrame([Labels.iloc[j+WindowSize]])])
            #Use np.flatten()
        WindowFeatures = pd.np.append(WindowFeatures,WindowFeatures_scenario,axis=0)
        Labels_final = pd.concat([Labels_final, Labels_scenario])
    
    return WindowFeatures, Labels_final

def GetTestAndTrainDataOwnship(scenarios, TestScenario, WindowSize=4):
    # Remove the test scenario from the training set
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    FeatureClass = 'OwnshipData'
    
    #Read the training features
    NumericFeatures, Labels, StartID, EndID = GetFeatures(TrainScenarios,FeatureClass)
    ScaledNumericFeatures = np.copy(NumericFeatures)
    # Center and scale the training features
    for i in range(17):
        ScaledNumericFeatures[:,i] = (NumericFeatures[:,i]-np.mean(NumericFeatures[:,i]))/np.std(NumericFeatures[:,i])
    Means = np.mean(NumericFeatures[:,0:17],axis=0)
    Stds = np.std(NumericFeatures[:,0:17],axis=0)
    # Create the windowed training features
    WindowFeatures,Labels_final = CreateWindowFeatures(ScaledNumericFeatures, Labels, StartID, EndID, WindowSize)
    Labels_final = np.array(Labels_final).flatten()
    
    #Read the test scenario features
    TestNumericFeatures, TestLabels, TestStartID, TestEndID = GetFeatures(TestScenario, FeatureClass)
    ScaledTestFeatures = np.copy(TestNumericFeatures)
    # Transform as per the linear transform applied to training data
    ScaledTestFeatures[:,0:17] = (TestNumericFeatures[:,0:17] - Means)/Stds
    # Create the windowed test features
    WindowFeatures_test, Labels_final_test = CreateWindowFeatures(ScaledTestFeatures, TestLabels, TestStartID, TestEndID, WindowSize)
    Labels_final_test = np.array(Labels_final_test).flatten()
    
    return WindowFeatures, Labels_final, WindowFeatures_test, Labels_final_test

def GetTestAndTrainDataOwnshipWingman(scenarios, TestScenario, WindowSize=5):
        # Remove the test scenario from the training set
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    FeatureClass = 'OwnshipWingmanData'
    
    #Read the training features
    NumericFeatures, Labels, StartID, EndID = GetFeatures(TrainScenarios,FeatureClass)
    ScaledNumericFeatures = np.copy(NumericFeatures)
    
    # Center and scale the continuos features to get mean 0 std 1
    Means = np.mean(NumericFeatures[:,0:20],axis=0)
    Stds = np.std(NumericFeatures[:,0:20],axis=0)
    ScaledNumericFeatures = (ScaledNumericFeatures[:,0:20]-Means)/Stds
    
    WindowFeatures,Labels_final = CreateWindowFeatures(ScaledNumericFeatures, Labels, StartID, EndID, WindowSize)
    Labels_final = np.array(Labels_final).flatten()
    
    TestNumericFeatures, TestLabels, TestStartID, TestEndID = GetFeatures(TestScenario, FeatureClass)
    ScaledTestFeatures = np.copy(TestNumericFeatures)
    ScaledTestFeatures = (TestNumericFeatures[:,0:20]-Means)/Stds
    
    WindowFeatures_test, Labels_final_test = CreateWindowFeatures(ScaledTestFeatures, TestLabels, TestStartID, TestEndID, WindowSize)
    Labels_final_test = np.array(Labels_final_test).flatten()
    
    return WindowFeatures, Labels_final, WindowFeatures_test, Labels_final_test

if __name__ == '__main__':
    scenarios = ['4C']
    FeatureClass = 'OwnshipData'
    players = ['Cool21', 'Cool22']
    WindowSize=5
    
    NumericFeatures, Labels, StartID, EndID = GetFeatures(scenarios,FeatureClass)
    WindowFeatures, Labels_final = CreateWindowFeatures(NumericFeatures, Labels, StartID, EndID, WindowSize)
    
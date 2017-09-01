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




def GetFeatures(scenarios, FeatureType):
    
    #define data path here
    path = '/home/ajshah/Dropbox (MIT)/LM Data/Data2'
    
    
    Features = pd.DataFrame()
    StartID = []
    EndID = []
    
    
        
    for scenario in scenarios:
        if scenario == '1A':
            players = ['Cool22']  #Discarding data to Cool21 in 1A
        else:
            players = ['Cool21','Cool22']
        for player in players:
            
            filename = path + '/' + FeatureType+'/'+scenario+'_'+player+'.pkl'
            data = pd.read_pickle(filename)
            
            NewFeatures = data
            NewFeatures = NewFeatures.ix[:,NewFeatures.columns!='Time']
            if scenario == '4C' and player == 'Cool21':
                NewFeatures = NewFeatures.iloc[17:,:]
            StartID.append(Features.shape[0])
            Features = pd.concat([Features,NewFeatures])
            EndID.append(Features.shape[0])

    #Features['NextWPIndex'] = Features['NextWPIndex'].astype('category')
    #Features['NextWPIndex'] = pd.Categorical(Features['NextWPIndex'] , categories = [0,1,2,3,4,5,6,7,8,9,10])
    Features.reset_index(drop=True,inplace=True)
    
    if FeatureType == 'OwnshipFlightPlanData':
        Features['NextWPIndex'] = pd.Categorical(Features['NextWPIndex'],categories=[0,1,2,3,4,5,6,7,8,9,10])
    
    if FeatureType == 'CommsData':
        Features['Comms'] = pd.Categorical(Features['Comms'],categories = [0,1])
    
    if FeatureType == 'OwnshipWeaponsData':
        Features['Weapons'] = pd.Categorical(Features['Weapons'], categories=[0,1])
    
    if FeatureType == 'LabelData':
        Features['Label'] = pd.Categorical(Features['Label'], categories = ['Push','Legs','OnTarget','Egress','ThreatIdentification','ThreatAvoidanceMitigation'])
    
    return Features, StartID, EndID






def GetTestAndTrainData(scenarios, TestScenario, OwnshipData=True, WingmanData=False, FlightPlanData=True, WeaponsData=True, CommsData=True, preprocess = True):
    
    TrainingScenarios = list(set(scenarios) - set(TestScenario))
    
    #Gather training Data
    TrainingFeatures = pd.DataFrame()
    
    OwnshipFeatures, TrainStartID, TrainEndID = GetFeatures(TrainingScenarios, 'OwnshipData')
    Offsets = np.mean(OwnshipFeatures)
    Scale = np.std(OwnshipFeatures)
    #OwnshipFeatures = (OwnshipFeatures - Offsets)/Scale
    TrainingFeatures = OwnshipFeatures
    
    if WingmanData==True:
        WingmanFeatures, TrainStartID, TrainEndID = GetFeatures(TrainingScenarios, 'WingmanData')
        WingmanOffsets = np.mean(WingmanFeatures)
        WingmanScale = np.std(WingmanFeatures)
        #WingmanFeatures = (WingmanFeatures - WingmanOffsets)/WingmanScale
        TrainingFeatures = pd.concat([TrainingFeatures, WingmanFeatures],axis=1, join='outer')
        Offsets = pd.concat([Offsets, WingmanOffsets])
        Scale = pd.concat([Scale, WingmanScale])
    
    if FlightPlanData==True:
        FlightPlanFeatures, TrainStartID, TrainEndID = GetFeatures(TrainingScenarios, 'OwnshipFlightPlanData')
        FlightPlanFeatures_onehot = pd.get_dummies(FlightPlanFeatures)
        
        FlightPlanOffsets = np.mean(FlightPlanFeatures_onehot)
        FlightPlanOffsets[FlightPlanOffsets.index] = 0
        FlightPlanOffsets[FlightPlanFeatures.select_dtypes(exclude=['category']).columns] = np.mean(FlightPlanFeatures[FlightPlanFeatures.select_dtypes(exclude=['category']).columns])
        
        FlightPlanScale = np.std(FlightPlanFeatures_onehot)
        FlightPlanScale[FlightPlanScale.index] = 1
        FlightPlanScale[FlightPlanFeatures.select_dtypes(exclude=['category']).columns] = np.std(FlightPlanFeatures[FlightPlanFeatures.select_dtypes(exclude=['category']).columns])
        
        #FlightPlanFeatures_onehot = (FlightPlanFeatures_onehot - FlightPlanOffsets)/FlightPlanScale
        
        TrainingFeatures = pd.concat([TrainingFeatures, FlightPlanFeatures_onehot], axis=1, join='outer')
        Offsets = pd.concat([Offsets, FlightPlanOffsets])
        Scale = pd.concat([Scale, FlightPlanScale])
        
    if WeaponsData==True:
        WeaponsFeatures, TrainStartID, TrainEndID = GetFeatures(TrainingScenarios, 'OwnshipWeaponsData')
        WeaponsFeatures_onehot = pd.get_dummies(WeaponsFeatures)
        
        WeaponsOffsets = np.mean(WeaponsFeatures_onehot)
        WeaponsOffsets[WeaponsOffsets.index] = 0
        WeaponsOffsets[WeaponsFeatures.select_dtypes(exclude=['category']).columns] = np.mean(WeaponsFeatures[WeaponsFeatures.select_dtypes(exclude=['category']).columns])
        
        WeaponsScale = np.std(WeaponsFeatures_onehot)
        WeaponsScale[WeaponsScale.index] = 1
        WeaponsScale[WeaponsFeatures.select_dtypes(exclude=['category']).columns] = np.std(WeaponsFeatures[WeaponsFeatures.select_dtypes(exclude=['category']).columns])
        
        #WeaponsFeatures_onehot = (WeaponsFeatures_onehot - WeaponsOffsets)/WeaponsScale
        TrainingFeatures = pd.concat([TrainingFeatures, WeaponsFeatures_onehot], axis=1, join='outer')
        Offsets = pd.concat([Offsets, WeaponsOffsets])
        Scale = pd.concat([Scale, WeaponsScale])
    
    if CommsData == True:
        CommsFeatures, TrainingStartID, TraininEndID = GetFeatures(TrainingScenarios, 'CommsData')
        CommsFeatures_onehot = pd.get_dummies(CommsFeatures)
        
        CommsOffsets = np.mean(CommsFeatures_onehot)
        CommsOffsets[CommsOffsets.index] = 0
        
        CommsScale = np.std(CommsFeatures_onehot)
        CommsScale[CommsScale.index] = 1
        
        TrainingFeatures = pd.concat([TrainingFeatures, CommsFeatures_onehot],axis=1, join='outer')
        Offsets = pd.concat([Offsets, CommsOffsets])
        Scale = pd.concat([Scale, CommsScale])
    
    TrainingLabels, TrainStartID, TrainEndID = GetFeatures(TrainingScenarios, 'LabelData')
    
    if preprocess==True:
        TrainingFeatures = (TrainingFeatures-Offsets)/Scale
    #Create test features
    TestFeatures = pd.DataFrame()
    
    OwnshipFeatures, TestStartID, TestEndID = GetFeatures(TestScenario, 'OwnshipData')
    TestFeatures = OwnshipFeatures
    
    if WingmanData == True:
        WingmanFeatures, TestStartId, TestEndID = GetFeatures(TestScenario, 'WingmanData')
        TestFeatures = pd.concat([TestFeatures, WingmanFeatures],axis=1, join='outer')
    
    if FlightPlanData == True:
        FlightPlanFeatures, TestStartID, TestEndID = GetFeatures(TestScenario, 'OwnshipFlightPlanData')
        FlightPlanFeatures_onehot = pd.get_dummies(FlightPlanFeatures)
        TestFeatures = pd.concat([TestFeatures, FlightPlanFeatures_onehot],axis=1, join='outer')
        
    if WeaponsData == True:
        WeaponsFeatures, TestStartID, TestEndID = GetFeatures(TestScenario, 'OwnshipWeaponsData')
        WeaponsFeatures_onehot = pd.get_dummies(WeaponsFeatures)
        TestFeatures = pd.concat([TestFeatures, WeaponsFeatures_onehot],axis=1, join='outer')
        
    if CommsData == True:
        CommsFeatures, TestStartId, TestEndID = GetFeatures(TestScenario, 'CommsData')
        CommsFeatures_onehot = pd.get_dummies(CommsFeatures)
        TestFeatures = pd.concat([TestFeatures, CommsFeatures_onehot],axis=1, join='outer')
    
    if preprocess==True:
        TestFeatures = (TestFeatures-Offsets)/Scale
        
    
    TestLabels, TestStartID, TestEndID = GetFeatures(TestScenario, 'LabelData')
    
    return TrainingFeatures, TrainingLabels, TestFeatures, TestLabels, Offsets, Scale, TrainStartID, TrainEndID, TestStartID, TestEndID






def GetScenarioData(Scenario, Scale, Offset, WingmanData=False, FlightPlanData = True, WeaponsData = True, CommsData = True, preprocess = True):
    
    Features = pd.DataFrame()
    OwnshipFeatures, StartID, EndID = GetFeatures(Scenario, 'OwnshipData')
    Features = OwnshipFeatures
    
    if WingmanData == True:
        WingmanFeatures, StartID, EndID = GetFeatures(Scenario, 'WingmanData')
        Features = pd.concat([Features, WingmanFeatures],axis=1, join='outer')
    
    if FlightPlanData == True:
        FlightPlanFeatures, StartID, EndID = GetFeatures(Scenario, 'OwnshipFlightPlanData')
        FlightPlanFeatures_onehot = pd.get_dummies(FlightPlanFeatures)
        Features = pd.concat([Features, FlightPlanFeatures_onehot],axis=1, join='outer')
        
    if WeaponsData == True:
        WeaponsFeatures, StartID, EndID = GetFeatures(Scenario, 'OwnshipWeaponsData')
        WeaponsFeatures_onehot = pd.get_dummies(WeaponsFeatures)
        Features = pd.concat([Features, WeaponsFeatures_onehot],axis=1, join='outer')
        
    if CommsData == True:
        CommsFeatures, StartId, EndID = GetFeatures(Scenario, 'CommsData')
        CommsFeatures_onehot = pd.get_dummies(CommsFeatures)
        Features = pd.concat([Features, CommsFeatures_onehot],axis=1, join='outer')
    
    if preprocess==True:
        Features = (Features-Offsets)/Scale
        
    
    Labels, StartID, EndID = GetFeatures(Scenario, 'LabelData')
    
    return Features, Labels, StartID, EndID






def GenerateWindowedData(Features, Labels, StartID, EndID, WindowSize=5, RNNMode = False):
    NumericFeatures = np.array(Features)
    WindowFeatures = pd.np.zeros([0,WindowSize*NumericFeatures.shape[1]])
    Labels_final = pd.DataFrame()
    OutStartID = []
    OutEndID = []
    
    for i in range(len(StartID)):
        WindowFeatures_scenario = pd.np.zeros([EndID[i] - WindowSize - StartID[i],WindowFeatures.shape[1]])
        Labels_scenario = pd.DataFrame()
        for (index,j) in enumerate(range(StartID[i], EndID[i]-WindowSize)):
            FeatureSet = NumericFeatures[j:j+WindowSize,:]
            FlatFeatureSet = FeatureSet.flatten()
            WindowFeatures_scenario[index] = FlatFeatureSet
            Labels_scenario = pd.concat([Labels_scenario, pd.DataFrame([Labels.iloc[j+WindowSize,:]])])
            #Use np.flatten()
        
        OutStartID.append(WindowFeatures.shape[0])
        WindowFeatures = pd.np.append(WindowFeatures,WindowFeatures_scenario,axis=0)
        OutEndID.append(WindowFeatures.shape[0])
        
        Labels_final = pd.concat([Labels_final, Labels_scenario])
    Labels_final[0] = pd.Categorical(Labels_final[0], categories = ['Push','Legs','OnTarget','Egress','ThreatIdentification','ThreatAvoidanceMitigation'])
    Labels_final.rename(columns={0:'Label'},inplace=True)
    
    if RNNMode == True:
        return WindowFeatures, Labels_final, OutStartID, OutEndID
        
    return WindowFeatures, Labels_final






def GenerateWindowedTestAndTrainData(scenarios, TestScenario, WindowSize=5, OwnshipData=True, WingmanData=False, FlightPlanData=True, WeaponsData=True, CommsData=True, preprocess = True, RNNMode = False):
    
    TrainingFeatures, TrainingLabels, TestFeatures, TestLabels, Offsets, Scale, TrainStartID, TrainEndID, TestStartID, TestEndID \
      = GetTestAndTrainData(scenarios, TestScenario, OwnshipData=OwnshipData, WingmanData=WingmanData, FlightPlanData=FlightPlanData, WeaponsData=WeaponsData, CommsData=CommsData, preprocess=preprocess)
      
    
    if RNNMode==False:
        WindowTrainingData, FinalTrainingLabels = GenerateWindowedData(TrainingFeatures, TrainingLabels, TrainStartID, TrainEndID, WindowSize=WindowSize, RNNMode=False)
      
        WindowTestData, FinalTestLabels = GenerateWindowedData(TestFeatures, TestLabels, TestStartID, TestEndID, WindowSize=WindowSize)
      
        return WindowTrainingData, FinalTrainingLabels, WindowTestData, FinalTestLabels
    else:
        
        WindowTrainingData, FinalTrainingLabels, OutTrainStartID, OutTrainEndID = GenerateWindowedData(TrainingFeatures, TrainingLabels, TrainStartID, TrainEndID, WindowSize=WindowSize, RNNMode=True)
        
        WindowTestData, FinalTestLabels, OutTestStartID, OutTestEndID = GenerateWindowedData(TestFeatures, TestLabels, TestStartID, TestEndID, WindowSize=WindowSize, RNNMode=True)
        
        return WindowTrainingData, FinalTrainingLabels, WindowTestData, FinalTestLabels, OutTrainStartID, OutTrainEndID, OutTestStartID, OutTestEndID






if __name__ == '__main__':
#    scenarios = ['4C']
#    FeatureClass = 'OwnshipData'
#    players = ['Cool21', 'Cool22']
#    WindowSize=5
#    
#    NumericFeatures, Labels, StartID, EndID = GetFeatures(scenarios,FeatureClass)
#    WindowFeatures, Labels_final = CreateWindowFeatures(NumericFeatures, Labels, StartID, EndID, WindowSize)

    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4C']
    #Scenarios = ['2A']
    TestScenario = ['3A']
    #TrainingFeatures, TrainingLabels, TestFeatures, TestLabels, Offsets, Scale, TrainStartID, TrainEndID, TestStartID, TestEndID = GetTestAndTrainData(Scenarios, TestScenario, FlightPlanData=True, WingmanData=False, WeaponsData=False, preprocess=True)
    #TrainX, TrainY = GenerateWindowedData(TrainingFeatures, TrainingLabels, TrainStartID, TrainEndID, WindowSize=5)
    #TestX, TestY = GenerateWindowedData(TestFeatures, TestLabels, TestStartID, TestEndID, WindowSize=5)
    TrainX, TrainY, TestX, TestY, TrainStartID, TrainEndID, TestStartID, TestEndID = GenerateWindowedTestAndTrainData(Scenarios, TestScenario, WindowSize=5, WingmanData=True, RNNMode=True)
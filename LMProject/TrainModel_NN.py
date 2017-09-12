#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:54:51 2017

@author: ajshah
"""

import pandas as pd
import numpy as np
from PrepareFeatures import *
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.activations import softmax
from keras.utils import plot_model
from keras.optimizers import adam
from keras import callbacks
import pickle
from itertools import product
import os

path = '/home/ajshah/Dropbox (MIT)/LM Data/Data2/'

def CreateFeatureClass(WingmanData=True, FlightPlanData=True, WeaponsData=True, CommsData=True):
    
    FeatureClass = {}
    FeatureClass['WingmanData'] = WingmanData
    FeatureClass['FlightPlanData'] = FlightPlanData
    FeatureClass['WeaponsData'] = WeaponsData
    FeatureClass['CommsData'] = CommsData
    
    return FeatureClass

def GetData(scenarios, TestScenario, FeatureClass, WindowSize=5, onehot=False, returnDataFrame = False):
    
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    WingmanData = FeatureClass['WingmanData']
    FlightPlanData = FeatureClass['FlightPlanData']
    WeaponsData = FeatureClass['WeaponsData']
    CommsData = FeatureClass['CommsData']
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GenerateWindowedTestAndTrainData(TrainScenarios, TestScenario, WindowSize=WindowSize,
                                                                    WingmanData=WingmanData, FlightPlanData = FlightPlanData,
                                                                    WeaponsData=WeaponsData, CommsData=CommsData)
    if returnDataFrame == True:
        return XTrain, YTrain, XTest, YTest, Offsets, Scale
    
    if onehot==False:
        YTrain = np.array(YTrain).ravel()
        YTest = np.array(YTest).ravel()
    else:
        YTrain = np.array(pd.get_dummies(YTrain))
        YTest = np.array(pd.get_dummies(YTest))
    
    return XTrain, YTrain, XTest, YTest, Offsets, Scale

def TrainNN(XTrain, YTrain, BatchSize=100):
    
    #Define the NN architecture here
    NInputFeatures = XTrain.shape[1]
    Ntargets = YTrain.shape[1]
    
    NUnits = [NInputFeatures, NInputFeatures,100, 50,25]
    
    model = Sequential()
    
    model.add(Dense(units=NUnits[0], input_shape=(NInputFeatures,)))
    
    model.add(Dense(units = NUnits[1]))
    
    for i in range(2,len(NUnits)):
        model.add(Dense(units=NUnits[i], activation='relu'))
    
    model.add(Dense(Ntargets))
    model.add(Activation('softmax'))
    
    model.compile(loss = 'categorical_crossentropy', optimizer = adam(lr=0.001), metrics = ['accuracy'])
    History = model.fit(XTrain, YTrain, batch_size = BatchSize, epochs=20, validation_split=0.05)
    
    return model, History.history

def TrainAndEvalNN(Scenarios, TestScenario, FeatureClass, WindowSize=5, BatchSize=100):
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale = GetData(Scenarios, TestScenario, FeatureClass, WindowSize=5, returnDataFrame=True)
    
    YTrain_onehot = np.array(pd.get_dummies(YTrain))
    YTest_onehot = np.array(pd.get_dummies(YTest))
    
    LabelList = YTrain['Label'].cat.categories
    
    
    model, History = TrainNN(XTrain, YTrain_onehot, BatchSize=BatchSize)
    TrainAcc = History['acc'][-1]
    
    metrics = model.evaluate(XTest,YTest_onehot)
    TestAcc = metrics[1]
    
    PredictedLabels_onehot = model.predict(XTest)
    
    
    MaxID = np.argmax(PredictedLabels_onehot,axis=1)
    PredictedLabels = pd.DataFrame()
    PredictedLabels['Label'] = pd.Categorical(np.array(LabelList[MaxID]),categories=LabelList)
    
    #TestAcc2 = np.mean(np.array(PredictedLabels['Label']) == np.array(YTest['Label']))
    
    return model, TrainAcc, TestAcc, PredictedLabels, Offsets, Scale
    

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, BatchSize=100, SaveResult=False, filename='NNResults',
          dirname = 'NNModels'):
    #Determine the filename and the directory name first
    
    i=1
    if os.path.exists(path + filename+'.pkl'):
        filenameNew = filename+'_'+str(i)
        while os.path.exists(path + filenameNew+'.pkl'):
            i=i+1
            filenameNew = filename+'_'+str(i)
    else:
        filenameNew = filename

    filenameNew = filenameNew+'.pkl'
    if SaveResult == True:
        open(path+filenameNew,'wb')
    
    i=1
    if os.path.exists(path + dirname):
        dirnameNew = dirname+'_'+str(i)
        while os.path.exists(path + dirnameNew):
            i=i+1
            dirnameNew = dirname+'_'+str(i)
    else:
        dirnameNew = dirname
    if SaveResult==True:
        os.mkdir(path+dirnameNew)
    
    Models = {}
    TrainAccs = {}
    TestAccs = {}
    PredLabelsTest = {}
    
    for TestScenario in TestScenarios:
        
        model, TrainAcc, TestAcc, PredLabels, Offsets, Scale = TrainAndEvalNN(Scenarios, [TestScenario], FeatureClass,
                                                                              WindowSize=WindowSize, BatchSize=BatchSize,)
        
        # save model in directory
        ModelFileName = path + dirnameNew + '/' + TestScenario + '.h5'
        if SaveResult==True:
            model.save(ModelFileName)
        
        #Save model metadata
        DataFileName = path + dirnameNew + '/' + TestScenario + '.pkl'
        ModelData = dict()
        ModelData['WindowSize'] = WindowSize
        ModelData['Offsets'] = Offsets
        ModelData['Scale'] = Scale
        ModelData['TrainAcc'] = TrainAcc
        ModelData['TestAcc'] =TestAcc
        ModelData['PredLabels'] = PredLabels
        ModelData['FeatureClass'] = FeatureClass
        if SaveResult==True:
            with open(DataFileName,'wb') as file:
                pickle.dump(ModelData,file)
        
        Models[TestScenario] = ModelFileName[0:-3]
        TrainAccs[TestScenario] = TrainAcc
        TestAccs[TestScenario] = TestAcc
        PredLabelsTest[TestScenario] = PredLabels
        
    
    OutData = dict()
    OutData['Models'] = Models
    OutData['TrainingAccuracies'] = TrainAccs
    OutData['TestAccuracies'] = TestAccs
    OutData['PredictedTestLabels'] = PredLabelsTest
    OutData['WindowSize'] = WindowSize
    OutData['BatchSize'] = BatchSize
    if SaveResult==True:
        with open(path+filenameNew, 'wb') as file:
            pickle.dump(OutData, file)


    
    return OutData
    

#def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, BatchSize=100):
#    models = {}
#    Test_accs = []
#    y_pred_labels = {}
#
#    for TestScenario in TestScenarios:
#        
#        new_model,new_Test_acc,new_y_pred_labels,LabelDict = TrainRNN(Scenarios, [TestScenario], FeatureClass, WindowSize, BatchSize)
#        
#        filename = path + '/' + 'NNModels/Model_'+str(WindowSize)+'_'+str(BatchSize)+'_'+TestScenario+'.h5'
#        DatFilename = path + '/' + 'NNModels/Model_'+str(WindowSize)+'_'+str(BatchSize)+'_'+TestScenario+'.pkl'
#        
#        new_model.save(filename)
#        
#        with open(DatFilename,'wb') as file:
#            pickle.dump({'Test_accuracy':new_Test_acc, 'Test_predictions':new_y_pred_labels, 'LabelDictionary':LabelDict},file)
#            
#        models[TestScenario] = filename
#        Test_accs.append(new_Test_acc)
#        y_pred_labels[TestScenario] = new_y_pred_labels
#        
#    return models, Test_accs, y_pred_labels

def GridSearch(Scenarios, TestScenarios, FeatureClass, WindowSizes=[2,5,10], BatchSizes=[50,500]):
    TestAccs = {}
    MeanTestAccs = {}
    for (WindowSize,BatchSize) in product(WindowSizes,BatchSizes):
        
        newModels, newTestAccs, NewPredLabels = LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize, BatchSize)
        
        TestAccs[(WindowSize,BatchSize)] = newTestAccs
        newMeanTestAccs = np.mean(np.array(newTestAccs))
        MeanTestAccs[(WindowSize,BatchSize)] = newMeanTestAccs
    return TestAccs, MeanTestAccs

if __name__ == '__main__':
    
#     #Test single scenario run
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenario = ['1A']
#    model, test_acc, y_pred_labels, LabelDict = TrainRNN(Scenarios, TestScenario, 'OwnshipData')

    # Test LOOCV
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    FeatureClass = 'OwnshipWingmanData'
#    models, Test_accs, y_pred_labels = LOOCV(Scenarios, TestScenarios, FeatureClass=FeatureClass)
#    with open('NNResults_'+FeatureClass+'.pkl','wb') as file:
#        pickle.dump({'Models':models, 'TestAccuracies':Test_accs, 'PredictedLabels':y_pred_labels},file)

##     #Test GridSearch
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestAccs, MeanTestAccs = GridSearch(Scenarios, TestScenarios, 'OwnshipData')

    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4C']
    TestScenarios = ['1A']
    FeatureClass = CreateFeatureClass(WingmanData=False)
    #XTrain, YTrain, XTest, YTest, Offsets, Scale = GetData(Scenarios, TestScenarios, FeatureClass, WindowSize=2,returnDataFrame=True)
    #Output = TrainAndEvalNN(Scenarios, TestScenarios, FeatureClass)
    #model, History = TrainNN(XTrain, YTrain, BatchSize=100)
    OutData = LOOCV(Scenarios, TestScenarios, FeatureClass, SaveResult=False)
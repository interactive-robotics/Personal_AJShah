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

path = '/home/ajshah/Dropbox (MIT)/LM Data/Data'

def TrainRNN(scenarios, TestScenario, FeatureClass, WindowSize=5, BatchSize=100):
#Prepare the data

    TrainScenarios = list(set(scenarios) - set(TestScenario))
    
    if FeatureClass == 'OwnshipData':
        GetData = GetTestAndTrainDataOwnship
    elif FeatureClass == 'OwnshipWingmanData':
        GetData = GetTestAndTrainDataOwnshipWingman

    [X_train, y_train, X_test, y_test] = GetData(TrainScenarios, TestScenario, WindowSize = WindowSize)
    y_train= pd.Series(y_train)
    y_train = pd.Categorical(y_train, categories = list(set(y_train)))
    y_train = pd.Series(y_train)
    y_test = pd.Categorical(y_test, categories = list(set(y_train)))
    y_test = pd.Series(y_test)
    TrainSize = y_train.shape[0]
    y_big = y_train.append(y_test)
    y_big = pd.get_dummies(y_big)
    y_train_onehot = np.array(y_big.iloc[0:TrainSize,:])
    y_test_onehot  = np.array(y_big.iloc[TrainSize:,:])
    
    
    
    #Define a deep neural network
    
    NInputFeatures = X_train.shape[1]
    Ntargets = len(set(y_train))
    
    NUnits = [NInputFeatures, NInputFeatures,100, 50,25]
    
    model = Sequential()
    
    model.add(Dense(units=NUnits[0], input_shape=(NInputFeatures,)))
    
    model.add(Dense(units = NUnits[1]))
    
    for i in range(2,len(NUnits)):
        model.add(Dense(units=NUnits[i], activation='relu'))
    
    model.add(Dense(Ntargets))
    model.add(Activation('softmax'))
    
    model.compile(loss = 'categorical_crossentropy', optimizer = adam(lr=0.001), metrics = ['accuracy'])
    model.fit(X_train, y_train_onehot, batch_size = BatchSize, epochs = 20, validation_split = 0.05)
    
#    model.compile(loss = 'categorical_crossentropy', optimizer = adam(lr=0.0005), metrics = ['accuracy'])
#    model.fit(X_train, y_train_onehot, batch_size = 50, epochs = 20, validation_split = 0.05)
    metrics = model.evaluate(X_test, y_test_onehot)
    Test_acc = metrics[1]
    y_test_pred = model.predict(X_test)
    labelDict = np.array(y_big.columns)
    y_test_pred_int = np.argmax(y_test_pred, axis=1)
    y_pred_labels = [labelDict[val] for val in y_test_pred_int]
    
    return model, Test_acc, y_pred_labels, labelDict

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, BatchSize=100):
    models = {}
    Test_accs = []
    y_pred_labels = {}

    for TestScenario in TestScenarios:
        
        new_model,new_Test_acc,new_y_pred_labels,LabelDict = TrainRNN(Scenarios, [TestScenario], FeatureClass, WindowSize, BatchSize)
        
        filename = path + '/' + 'NNModels/Model_'+str(WindowSize)+'_'+str(BatchSize)+'_'+TestScenario+'.h5'
        DatFilename = path + '/' + 'NNModels/Model_'+str(WindowSize)+'_'+str(BatchSize)+'_'+TestScenario+'.pkl'
        
        new_model.save(filename)
        
        with open(DatFilename,'wb') as file:
            pickle.dump({'Test_accuracy':new_Test_acc, 'Test_predictions':new_y_pred_labels, 'LabelDictionary':LabelDict},file)
            
        models[TestScenario] = filename
        Test_accs.append(new_Test_acc)
        y_pred_labels[TestScenario] = new_y_pred_labels
        
    return models, Test_accs, y_pred_labels

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
    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
    FeatureClass = 'OwnshipWingmanData'
    models, Test_accs, y_pred_labels = LOOCV(Scenarios, TestScenarios, FeatureClass=FeatureClass)
    with open('NNResults_'+FeatureClass+'.pkl','wb') as file:
        pickle.dump({'Models':models, 'TestAccuracies':Test_accs, 'PredictedLabels':y_pred_labels},file)

##     #Test GridSearch
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestAccs, MeanTestAccs = GridSearch(Scenarios, TestScenarios, 'OwnshipData')
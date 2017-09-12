#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 20:42:53 2017

@author: ajshah
"""

import pandas as pd
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Input
from keras.layers.core import Masking
from keras.layers.recurrent import LSTM
from keras.activations import softmax
from keras.utils import plot_model
from keras.optimizers import adam,sgd
from keras import callbacks
from keras.layers.wrappers import TimeDistributed
#from PrepareRNNFeatures import *
from RNNDataParser import *
import pickle
from itertools import product
import numpy as np


def CreateFeatureClass(WingmanData=True, FlightPlanData=True, WeaponsData=True, CommsData=True):
    
    FeatureClass = {}
    FeatureClass['WingmanData'] = WingmanData
    FeatureClass['FlightPlanData'] = FlightPlanData
    FeatureClass['WeaponsData'] = WeaponsData
    FeatureClass['CommsData'] = CommsData
    
    return FeatureClass


def GetData(scenarios, TestScenario, FeatureClass, WindowSize=5, SeqSize=100):
    
    TrainScenarios = list(set(scenarios) - set(TestScenario))
    WingmanData = FeatureClass['WingmanData']
    FlightPlanData = FeatureClass['FlightPlanData']
    WeaponsData = FeatureClass['WeaponsData']
    CommsData = FeatureClass['CommsData']
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale, LabelList = PrepareRNNData(scenarios, TestScenario, WindowSize=WindowSize, SeqSize=SeqSize,
                                                  WingmanData=WingmanData, FlightPlanData=FlightPlanData, CommsData=CommsData,
                                                  WeaponsData=WeaponsData)
    
    
    
    return XTrain, YTrain, XTest, YTest, Offsets, Scale, LabelList


def TrainRNN(XTrain, YTrain, BatchSize=50, WindowSize=5):
    
    SeqSize = XTrain.shape[1]
    input1 = Input(shape=(SeqSize, XTrain.shape[2]))
    MaskedInput = Masking(mask_value=0)(input1)
    
    #Add dense layer to learn locally consistent behaviors
    DenseOut1 = TimeDistributed(Dense(3*int(XTrain.shape[2]/WindowSize), input_shape = (SeqSize,XTrain.shape[2])))(MaskedInput)
    DenseOut2 = TimeDistributed(Dense(int(XTrain.shape[2]/WindowSize), input_shape = (SeqSize,XTrain.shape[2]), activation='relu'))(DenseOut1)
    
    
    #possible add more dense layers here
    
    #Stack LSTMs on top of each other
    LSTMOut1 = LSTM(50, return_sequences = True)(DenseOut2)
    LSTMOut2 = LSTM(20, return_sequences = True)(LSTMOut1)
    LSTMOut3 = LSTM(16, return_sequences=True)(LSTMOut2)
    
    # Provide LSTM output to dense classification activations
    Dense2Out = TimeDistributed(Dense(YTrain.shape[2]))(LSTMOut3)
    # Generate predictions from softmax activations
    Predictions = TimeDistributed(Activation('softmax'))(Dense2Out)
    
    #Compile the model
    model = Model(inputs = [input1], outputs = [Predictions])
    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.005), metrics = ['accuracy'])
    model.fit(XTrain,YTrain, epochs = 50, validation_split=0.00, batch_size=BatchSize)
    
    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.0025), metrics = ['accuracy'])
    History = model.fit(XTrain,YTrain, epochs = 50, validation_split=0.00, batch_size=BatchSize)
    
    return model, History.history



def TrainAndEvalRNN(scenarios, TestScenario, FeatureClass, WindowSize=5, SeqSize=100):
    
    XTrain, YTrain, XTest, YTest, Offsets, Scale, LabelList = GetData(scenarios, TestScenario, FeatureClass, WindowSize=WindowSize,
                                                                      SeqSize=SeqSize)
    
    model, History = TrainRNN(XTrain, YTrain)
    TrainAcc = History['acc']
    
    TestAcc = model.evaluate(XTest, YTest)[1]
    
    PredictedLabels_onehot = model.predict(XTest)
    MaxID = np.argmax(PredictedLabels_onehot,axis=2)
    #MaxID = MaxID.flatten()
    
    return model, TrainAcc, TestAcc, MaxID, PredictedLabels_onehot




















#def TrainRNN(scenarios, TestScenatio, FeatureClass, WindowSize=5, SeqSize=100):
#    
#    #SeqSize = 400
#    #WindowSize = 5
#    SeqX_train, SeqY_train, SeqX_test, SeqY_test = ReadRNNData(scenarios, TestScenario, FeatureClass='OwnshipData', WindowSize=WindowSize, SeqSize=SeqSize)
#    
#    input1 = Input(shape=(SeqSize,SeqX_train.shape[2]))
#    MaskedInput = Masking(mask_value=0)(input1)
#    
#    #Add dense layer to learn locally consistent behaviors
#    DenseOut1 = TimeDistributed(Dense(3*int(SeqX_train.shape[2]/WindowSize), input_shape = (SeqSize,SeqX_train.shape[2])))(MaskedInput)
#    DenseOut2 =-TimeDistributed(Dense(int(SeqX_train.shape[2]/WindowSize), input_shape = (SeqSize,SeqX_train.shape[2])))(DenseOut1)
#    
#    #possible add more dense layers here
#    
#    #Stack LSTMs on top of each other
#    LSTMOut1 = LSTM(50, return_sequences = True)(DenseOut1)
#    LSTMOut2 = LSTM(20, return_sequences = True)(LSTMOut1)
#    LSTMOut3 = LSTM(16, return_sequences=True)(LSTMOut2)
#    
#    # Provide LSTM output to dense classification activations
#    Dense2Out = TimeDistributed(Dense(SeqY_train.shape[2]))(LSTMOut2)
#    # Generate predictions from softmax activations
#    Predictions = TimeDistributed(Activation('softmax'))(Dense2Out)
#    
#    #Compile the model
#    model = Model(inputs = [input1], outputs = [Predictions])
#    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.005), metrics = ['accuracy'])
#    model.fit(SeqX_train,SeqY_train, epochs = 50, validation_split=0.00, batch_size=50)
#    
#    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.0025), metrics = ['accuracy'])
#    model.fit(SeqX_train,SeqY_train, epochs = 50, validation_split=0.00, batch_size=50)
#    
#    TestAcc = model.evaluate(SeqX_test,SeqY_test)[1]
#    Y_test_predictions = model.predict(SeqX_test)
#    
#    return model, TestAcc, Y_test_predictions

def TrainRNN2(scenarios, TestScenatio, FeatureClass, WindowSize=5, SeqSize=100):
    
    #SeqSize = 400
    #WindowSize = 5
    SeqX_train, SeqY_train, SeqX_test, SeqY_test = ReadRNNData(scenarios, TestScenario, FeatureClass='OwnshipData', WindowSize=WindowSize, SeqSize=SeqSize)
    
    input1 = Input(shape=(SeqSize,SeqX_train.shape[2]))
    MaskedInput = Masking(mask_value=0)(input1)
    
    #Add dense layer to learn locally consistent behaviors
    
    #possible add more dense layers here
    
    #Stack LSTMs on top of each other
    LSTMOut1 = LSTM(25, return_sequences = True)(MaskedInput)

    # Provide LSTM output to dense classification activations
    Dense2Out = TimeDistributed(Dense(SeqY_train.shape[2]))(LSTMOut1)
    # Generate predictions from softmax activations
    Predictions = TimeDistributed(Activation('softmax'))(Dense2Out)
    
    #Compile the model
    model = Model(inputs = [input1], outputs = [Predictions])
    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.005), metrics = ['accuracy'])
    model.fit(SeqX_train,SeqY_train, epochs = 200, validation_split=0.00, batch_size=10)
    
    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.0025), metrics = ['accuracy'])
    model.fit(SeqX_train,SeqY_train, epochs = 200, validation_split=0.00, batch_size=10)
    
    TestAcc = model.evaluate(SeqX_test,SeqY_test)[1]
    Y_test_predictions = model.predict(SeqX_test)
    
    return model, TestAcc, Y_test_predictions

def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SeqSize=100):
    models = {}
    Test_accs = []
    y_pred_labels = {}

    for TestScenario in TestScenarios:
        
        new_model,new_Test_acc,new_y_pred_labels,= TrainRNN(Scenarios, [TestScenario], FeatureClass, WindowSize, SeqSize)
        
        filename = 'RNNModels/Model_'+str(WindowSize)+'_'+str(SeqSize)+'_'+TestScenario+'.h5'
        DatFilename = 'RNNModels/Model_'+str(WindowSize)+'_'+str(SeqSize)+'_'+TestScenario+'.pkl'
        
        new_model.save(filename)
        
        LabelDict = np.array(['Push','Legs','OnTarget','Egress','ThreatIdentification','ThreatAvoidanceMitigation'],dtype=object)
        
        with open(DatFilename,'wb') as file:
            pickle.dump({'Test_accuracy':new_Test_acc, 'Test_predictions':new_y_pred_labels, 'LabelDictionary':LabelDict},file)
            
        models[TestScenario] = filename
        Test_accs.append(new_Test_acc)
        y_pred_labels[TestScenario] = new_y_pred_labels
        
        
        #with open('RNNresults.pkl','wb') as file:
            #pickle.dump({'models':models, 'TestAccuracies':Test_accs, 'PredictedLabels':y_pred_labels, 'LabelDictionary':LabelDict},file)
        
    return models, Test_accs, y_pred_labels

def GridSearch(Scenarios, TestScenarios, FeatureClass, WindowSizes=[2,5,10], SeqSizes=[50,100,200]):
    TestAccs = {}
    MeanTestAccs = {}
    for (WindowSize,SeqSize) in product(WindowSizes,SeqSizes):
        
        newModels, newTestAccs, NewPredLabels = LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize, SeqSize)
        
        TestAccs[(WindowSize,SeqSize)] = newTestAccs
        newMeanTestAccs = np.mean(np.array(newTestAccs))
        MeanTestAccs[(WindowSize,SeqSize)] = newMeanTestAccs
    return TestAccs, MeanTestAccs


if __name__=='__main__':
    FeatureClass = CreateFeatureClass()
    #XTrain, YTrain, XTest, YTest, Offsets, Scale, LabelList = GetData(['1A'],['2A'],FeatureClass)
    #model, History = TrainRNN(XTrain,YTrain)
    model, TestAcc, TrainAcc, MaxID, PredictedLabels = TrainAndEvalRNN(['1A'],['2A'], FeatureClass)
    
    
    
    
#    scenarios = ['1A','1B','1C', '2A','2B','2C', '3A','3B','3C', '4A','4C']
#    TestScenario = ['2B']
#    model, TestAcc, Y_test_predictions = TrainRNN2(scenarios, TestScenario, FeatureClass = 'OwnshipData', WindowSize=10, SeqSize=500)
#    
#        # Test LOOCV
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    FeatureClass = 'OwnshipWingmanData'
#    models, Test_accs, y_pred_labels = LOOCV(Scenarios, TestScenarios, FeatureClass=FeatureClass)
#    with open('RNNResults_'+FeatureClass+'.pkl','wb') as file:
#        pickle.dump({'Models':models,'TestAccuracies':Test_accs, 'PredictedLabels':y_pred_labels},file)


##    
#    Scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestScenarios = ['1A','1B','1C','2A','2B','2C','3A','3B', '3C','4A','4C']
#    TestAccs, MeanTestAccs = GridSearch(Scenarios, TestScenarios, FeatureClass='OwnshipWingmanData', WindowSizes=[2,5,10], SeqSizes=[50,100,500])
#    with open('RNNGridSearchResults_'+FeatureClass+'.pkl','wb') as file:
#        pickle.dump({'TestAccuracies':TestAccs, 'MeanTestAccuracies':MeanTestAccs},file)
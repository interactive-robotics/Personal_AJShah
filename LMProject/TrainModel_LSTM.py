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

path = '/home/ajshah/Dropbox (MIT)/LM Data/Data2/'

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
    
    XTrain, YTrain, XTest, YTest, TrainSeqLen, TestSeqLen, Offsets, Scale, LabelList = PrepareRNNData(scenarios, TestScenario, WindowSize=WindowSize, SeqSize=SeqSize,
                                                  WingmanData=WingmanData, FlightPlanData=FlightPlanData, CommsData=CommsData,
                                                  WeaponsData=WeaponsData)
    
    
    
    return XTrain, YTrain, XTest, YTest, TrainSeqLen, TestSeqLen, Offsets, Scale, LabelList


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
    model.fit(XTrain,YTrain, epochs = 10, validation_split=0.00, batch_size=BatchSize)
    
    model.compile(loss = 'categorical_crossentropy',optimizer = adam(lr=0.0025), metrics = ['accuracy'])
    History = model.fit(XTrain,YTrain, epochs = 10, validation_split=0.00, batch_size=BatchSize)
    
    return model, History.history



def TrainAndEvalRNN(scenarios, TestScenario, FeatureClass, WindowSize=5, SeqSize=100):
    
    XTrain, YTrain, XTest, YTest, TrainSeqLen, TestSeqLen, Offsets, Scale, LabelList = GetData(scenarios, TestScenario, FeatureClass, WindowSize=WindowSize,
                                                                      SeqSize=SeqSize)
    
    model, History = TrainRNN(XTrain, YTrain)
    TrainAcc = History['acc'][-1]
    
    TestAcc = model.evaluate(XTest, YTest)[1]
    
    PredictedLabels_onehot = model.predict(XTest)
    #MaxID = np.argmax(PredictedLabels_onehot,axis=2)
    #MaxID = MaxID.flatten()
    
    return model, TrainAcc, TestAcc, PredictedLabels_onehot, TestSeqLen, Offsets, Scale, LabelList



def GatherPredictions(PredictedLabels_onehot, SeqLen, LabelList):
    MaxID_tensor = np.argmax(PredictedLabels_onehot, axis=2)
    MaxID = np.empty(shape = (0), dtype=np.int32)
    unitsadded = []
    for i in range(len(SeqLen)):
        MaxID_Seq = MaxID_tensor[i][0:SeqLen[i]]
        unitsadded.append(MaxID_Seq.shape)
        MaxID = np.append(MaxID, MaxID_Seq)
    PredictedLabels = pd.DataFrame()
    PredictedLabels['Label'] = pd.Categorical(LabelList[MaxID], categories = LabelList)
    
    return PredictedLabels



def LOOCV(Scenarios, TestScenarios, FeatureClass, WindowSize=5, SeqSize=100, SaveResult=False, filename='RNNResults',
          dirname = 'RNNModels'):
    #Determine the filename and the directory name first
    #path = '/home/ajshah/Dropbox (MIT)/LM Data/Data2/Results'
    
    i=1
    if os.path.exists(path + 'Results/' + filename+'.pkl'):
        filenameNew = filename+'_'+str(i)
        while os.path.exists(path + 'Results/' + filenameNew+'.pkl'):
            i=i+1
            filenameNew = filename+'_'+str(i)
    else:
        filenameNew = filename

    filenameNew = filenameNew+'.pkl'
    if SaveResult == True:
        open(path+ 'Results/' + filenameNew,'wb')
    
    i=1
    if os.path.exists(path + 'Results/' + dirname):
        dirnameNew = dirname+'_'+str(i)
        while os.path.exists(path +'Results/' + dirnameNew):
            i=i+1
            dirnameNew = dirname+'_'+str(i)
    else:
        dirnameNew = dirname
    if SaveResult==True:
        os.mkdir(path+ 'Results/' + dirnameNew)
    
    Models = {}
    TrainAccs = {}
    TestAccs = {}
    PredLabelsTest = {}
    
    for TestScenario in TestScenarios:
        
        model, TrainAcc, TestAcc, PredLabels, TestSeqLen, Offsets, Scale, LabelList = TrainAndEvalRNN(Scenarios, [TestScenario], FeatureClass,
                                                                              WindowSize=WindowSize, SeqSize=SeqSize)
        
        # save model in directory
        ModelFileName = path + 'Results/' + dirnameNew + '/' + TestScenario + '.h5'
        if SaveResult==True:
            model.save(ModelFileName)
        
        #Save model metadata
        DataFileName = path +'Results/' + dirnameNew + '/' + TestScenario + '.pkl'
        ModelData = dict()
        ModelData['WindowSize'] = WindowSize
        ModelData['SeqSize'] = SeqSize
        ModelData['Offsets'] = Offsets
        ModelData['Scale'] = Scale
        ModelData['TrainAcc'] = TrainAcc
        ModelData['TestAcc'] =TestAcc
        ModelData['PredLabels'] = PredLabels
        ModelData['FeatureClass'] = FeatureClass
        ModelData['LabelList'] = LabelList
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
    #OutData['BatchSize'] = BatchSize
    if SaveResult==True:
        with open(path + 'Results/' + filenameNew, 'wb') as file:
            pickle.dump(OutData, file)


    
    return OutData







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
    Scenarios = ['1A','1B','2A']
    TestScenarios = ['4C','4A']
    
    OutData = LOOCV(Scenarios, TestScenarios, FeatureClass, SaveResult=True)
    
    
    
#    XTrain, YTrain, XTest, YTest, TrainSeqLen, TestSeqLen, Offsets, Scale, LabelList = GetData(Scenarios,TestScenario,FeatureClass, SeqSize=500)
#    model, TrainAcc, TestAcc, PredictedLabels, Offsets, Scale, LabelList = TrainAndEvalRNN(Scenarios,TestScenario, FeatureClass,SeqSize=500)
#    PredictedLabels = GatherPredictions(PredictedLabels, TestSeqLen, LabelList)
#    TrueLabels = GatherPredictions(YTest, TestSeqLen, LabelList)
#    Accuracy = np.mean(np.array(PredictedLabels['Label']) == np.array(TrueLabels['Label']))
#    
    
    
    
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
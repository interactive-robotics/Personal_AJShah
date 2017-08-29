#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 17:23:18 2017

@author: ajshah
"""
import pickle
import pandas as pd
from PrepareFeatures import *
from itertools import product
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC,LinearSVC
import numpy as np

resultsPath = '/home/ajshah/Dropbox (MIT)/LM Data/Data/Results'
dataPath = path = '/home/ajshah/Dropbox (MIT)/LM Data/Data'
FeatureClass = 'OwnshipData'
ResultsFile = 'LinearSVCResults_OwnshipData_.pkl'


#Load example dataframe of the data of the given Class
datafilepath = dataPath + '/' + FeatureClass + '/' + '1A_Cool21.pkl'
data = pd.read_pickle(datafilepath)
fieldNames = data.columns

#Obtain the feature count for the model
Features,Labels,sid,eid = GetFeatures(['1A'],FeatureClass = FeatureClass)
nFeatures = Features.shape[1]

#Load results
filePath = resultsPath + '/' + FeatureClass + '/' + ResultsFile
with open(filePath,'rb') as file:
    ResultsData = pickle.load(file)
Models = ResultsData['Models']

#Load the featuremap
mapfilename = FeatureClass + '_' + 'FeatureMapping.pkl'
with open(mapfilename,'rb') as file:
    data = pickle.load(file)
FeatureMap = data['FeatureMap']

topPredictors = {}

topN = 10

for key in Models.keys():
    for j in range(len(Models[key].classes_)):
        ModelCoefs = Models[key].coef_[j,:]
        sortedModelCoefsIndex = np.argsort(-np.abs(ModelCoefs))
        TopIndices = sortedModelCoefsIndex[0:topN]
        TopFeatures = []
        for index in TopIndices:
            TopFeatures.append(FeatureMap[index%nFeatures])
        topPredictors[(key,Models[key].classes_[j])] = TopFeatures

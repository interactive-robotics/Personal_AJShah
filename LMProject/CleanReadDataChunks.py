#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 17:04:00 2017

@author: ajshah
"""

import pandas as pd
from scipy.interpolate import interp1d
import pickle

path = '/home/ajshah/Dropbox (MIT)/Data' #Define the path to the data folder here

def CreateFeatures(scenario):
    #scenario = '1A'
    filename = path + '/' +  'DataLogs/'+scenario+'.csv'
    chunks = pd.read_csv(filename,header=0,skiprows=[1,2], index_col=False, error_bad_lines=False, chunksize=100000)
    
    # Define the players (Aircrafts)
    Playernames = ['Cool21', 'Cool22']
    F16Data = dict()
    for player in Playernames:
        F16Data[player] = pd.DataFrame()
    
    # Define the object name for the scenario target
    if scenario in set(['1A','1B','1C']):
        target = 'TU-95'
        
    if scenario in set(['2A','2B','2C']):
        target = 'VEH_air_FuelTruck100LL'
        
    if scenario in set(['3A','3B','3C']):
        target= 'Fan_Song_Radar'
        
    if scenario in set(['4A','4B','4C']):
        target= 'T-72'
        
    Objects = [target,]
    ObjectData = dict()
    for Object in Objects:
        ObjectData[Object] = pd.DataFrame()
    
    #Obtain a list of all different object types being tracked
    NameSet = set()
    
    
    
    # Collect the data for the tracked objects
    for chunk in chunks:
        print(chunk.shape)
        NewSet = set(chunk['E:TITLE'])
        NameSet = NameSet.union(NewSet)
        
        for player in Playernames:
            data_player = chunk.ix[chunk['PLAYER NAME'].fillna('none')==player,:]
            F16Data[player] = pd.concat([F16Data[player], data_player.ix[data_player['E:TITLE']=='Lockheed Martin F-16C Weaponized',:]])
        
        for Object in Objects:
    #            ObjectData[Object] = chunk.ix[chunk['E:TITLE']==Object,:]
            ObjectData[Object] = pd.concat([ObjectData[Object], chunk.ix[chunk['E:TITLE']==Object,:]])
    
    # Extract the geolocation of the target using the ObjectData structure
    # Taking only the first element as the targets are stationary in all scenarios
    if scenario == '3B':
        with open('Data3B.pkl','rb') as file:
            data = pickle.load(file)
        TargetLat = data['TargetLat']
        TargetLon = data['TargetLon']
        TargetAlt = data['TargetAlt']
    else:
        TargetLat = ObjectData[target]['PLANE LATITUDE'].iloc[0]*0.3048 #Radians
        TargetLon = ObjectData[target]['PLANE LONGITUDE'].iloc[0]*0.3048 #Radians
        TargetAlt = ObjectData[target]['PLANE ALTITUDE'].iloc[0]
    
    #Make the data monotonic in time
    F16Data_time = dict()
    
    for player in Playernames:
        F16Data[player]['DELTAS'] = pd.np.insert(pd.np.diff(F16Data[player]['E:ABSOLUTE TIME']),0,0)
        F16Data_time[player] = F16Data[player].ix[F16Data[player]['DELTAS']>0,:]
        F16Data_time[player]['REL TIME'] = F16Data_time[player]['E:ABSOLUTE TIME'] - F16Data_time[player]['E:ABSOLUTE TIME'].iloc[0]
    
    
    
    # Identify the relevant raw features
    FeatureList = ['REL TIME', 'VELOCITY BODY X', 'VELOCITY BODY Y', 'VELOCITY BODY Z'
                   , 'ACCELERATION BODY X', 'ACCELERATION BODY Y', 'ACCELERATION BODY Z',
                   'ROTATION VELOCITY BODY X', 'ROTATION VELOCITY BODY Y', 'ROTATION VELOCITY BODY Z',
                   'GPS POSITION LAT', 'GPS POSITION LON', 'GPS POSITION ALT',
                   'PLANE PITCH DEGREES', 'PLANE BANK DEGREES', 'PLANE HEADING DEGREES TRUE',
                   'GPS WP DISTANCE', 'GPS WP BEARING', 'GPS FLIGHT PLAN WP INDEX' ]
    
    # Note that the GPS lat long are in degrees not radians
    
    IsCategorical = [0,0,0,0,
                     0,0,0,
                     0,0,0,
                     0,0,0,
                     0,0,0,
                     0,0,1]
    
    # Collect the relevant features
    rawData = dict()
    maxtimes = list()
    
    for player in Playernames:
        rawData[player] = F16Data_time[player]
        rawData[player].reset_index()
        maxtimes.append(max(rawData[player]['REL TIME']))
    
    max_time = min(maxtimes)
    
    
    # Sample the data given sampling time
    rawData_sampled = dict()
    for player in Playernames:
        rawData_sampled[player] = pd.DataFrame()
    SampleTime = 1
    times = pd.np.arange(0, max_time, SampleTime)
    
    for player in Playernames:
        rawData_sampled[player]['TIMES'] = times
        
        for (feature, isCat) in zip(FeatureList,IsCategorical):
            if isCat==0:
                f = interp1d(rawData[player]['REL TIME'], rawData[player][feature],kind='linear')
                rawData_sampled[player][feature] = f(rawData_sampled[player]['TIMES'])
            
            if isCat==1:
                f = interp1d(rawData[player]['REL TIME'], rawData[player][feature],kind='nearest')
                rawData_sampled[player][feature] = f(rawData_sampled[player]['TIMES'])
                

    
    # Read the annotation files for the players and add labels
    Annotations = dict()
    for player in Playernames:
        rawData_sampled[player]['PHASE LABEL'] = ''
        AnnotationFile = 'pilot_annotations/FlightAnnotation_'+player+'_'+scenario+'.csv'
        Annotations[player] = pd.read_csv(AnnotationFile,header=0, index_col=False, error_bad_lines=False)
        for i in range(rawData_sampled[player].shape[0]):
            for j in range(Annotations[player].shape[0]-1):
                #if rawData_sampled[player]['TIMES'].iloc[i] >= Annotations[player]['Time'].iloc[j] and rawData_sampled[player]['TIMES'].iloc[i] <= Annotations[player]['Time'].iloc[j+1]:
                if rawData_sampled[player]['TIMES'].iloc[i] >= Annotations[player]['Time'].iloc[j]:
                    rawData_sampled[player].loc[i,'PHASE LABEL'] = Annotations[player]['Phase'].iloc[j]
    
    
    
    FinalData  = dict()
    for player in Playernames:
        FinalData[player]=pd.DataFrame()
    
    FinalFeatureList = ['Time', 
                        'PosX:Target', 'PosY:Target', 'PosZ:Target',
                        'VelX:Body', 'VelY:Body', 'VelZ:Body',
                        'AccX:Body', 'AccY:Body', 'AccZ:Body',
                        'Yaw', 'Pitch', 'Roll',
                        'YawRate', 'PitchRate', 'RollRate',
                        'NextWPDist','NextWPHeading', 'NextWPIndex',
                        'PhaseLabels']
    
    REarth = 6371.0e3;
    for player in Playernames:
        relLat = pd.np.array(rawData_sampled[player]['GPS POSITION LAT']*pd.np.pi/180 - TargetLat)
        relLon = pd.np.array(rawData_sampled[player]['GPS POSITION LON']*pd.np.pi/180 - TargetLon)
        relZ = pd.np.array(rawData_sampled[player]['GPS POSITION ALT'] - TargetAlt)
        relX = relLat*REarth
        relY = relLon*REarth*pd.np.cos(TargetLat)
        FinalData[player]['Time'] = rawData_sampled[player]['TIMES']
        FinalData[player]['PosX:Target'] = relX
        FinalData[player]['PosY:Target'] = relY
        FinalData[player]['PosZ:Target'] = relZ
        FinalData[player]['VelX:Body'] = rawData_sampled[player]['VELOCITY BODY Z']
        FinalData[player]['VelY:Body'] = -rawData_sampled[player]['VELOCITY BODY X']
        FinalData[player]['VelZ:Body'] = -rawData_sampled[player]['VELOCITY BODY Y']
        FinalData[player]['AccX:Body'] = rawData_sampled[player]['ACCELERATION BODY Z']
        FinalData[player]['AccY:Body'] = -rawData_sampled[player]['ACCELERATION BODY X']
        FinalData[player]['AccZ:Body'] = -rawData_sampled[player]['ACCELERATION BODY Y']
        FinalData[player]['Yaw'] = rawData_sampled[player]['PLANE HEADING DEGREES TRUE']
        FinalData[player]['Pitch'] = rawData_sampled[player]['PLANE PITCH DEGREES']
        FinalData[player]['Roll'] = rawData_sampled[player]['PLANE BANK DEGREES']
        FinalData[player]['YawRate'] = -rawData_sampled[player]['ROTATION VELOCITY BODY Y']
        FinalData[player]['PitchRate'] = -rawData_sampled[player]['ROTATION VELOCITY BODY X']
        FinalData[player]['RollRate'] = rawData_sampled[player]['ROTATION VELOCITY BODY Z']
        FinalData[player]['NextWPDist'] = rawData_sampled[player]['GPS WP DISTANCE']
        FinalData[player]['NextWPHeading'] = rawData_sampled[player]['GPS WP BEARING']
        FinalData[player]['NextWPIndex'] = rawData_sampled[player]['GPS FLIGHT PLAN WP INDEX']
        FinalData[player]['Label'] = rawData_sampled[player]['PHASE LABEL']
        
    
    # Write the ownship data to the files
    for player in Playernames:
        filename = path + '/' + 'OwnshipData/'+scenario+'_'+player+'.pkl'
        FinalData[player].to_pickle(filename)
    
    # Generate Ownship+wingman features (only relative position)
    
    FinalWingmanFeature = dict()
    for player in Playernames:
        FinalWingmanFeature[player] = pd.DataFrame()
    
    for player in Playernames:
        OtherPlayers = [otherPlayer for otherPlayer in Playernames if otherPlayer!=player]
        
        OtherPlayer = OtherPlayers[0]
        P2Pos = FinalData[OtherPlayer].loc[:,['PosX:Target','PosY:Target','PosZ:Target']]
        P1Pos = FinalData[player].loc[:,['PosX:Target','PosY:Target','PosZ:Target']]
        relPos = pd.np.array(P2Pos - P1Pos)
        FinalWingmanFeature[player] = FinalData[player]
        FinalWingmanFeature[player]['WingX'] = relPos[:,0]
        FinalWingmanFeature[player]['WingY'] = relPos[:,1]
        FinalWingmanFeature[player]['WingZ'] = relPos[:,2]
        filename = path + '/' + 'OwnshipWingmanData/'+scenario+'_'+player+'.pkl'
        FinalWingmanFeature[player].to_pickle(filename)
    return FinalData, FinalWingmanFeature, TargetLat, TargetLon, TargetAlt, Annotations, F16Data_time

if __name__ =='__main__':
    #scenarios = ['1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4C']
    #scenarios=['4A','4C']
    scenarios=['1B']
    for scenario in scenarios:
        FinalData, FinalWingmanFeature,TargetLat,TargetLon,TargetAlt, Annotations, F16Data = CreateFeatures(scenario)
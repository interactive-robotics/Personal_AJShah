#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:15:57 2019

@author: ajshah
"""

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Softmax, Flatten
from keras.losses import categorical_crossentropy
from keras.optimizers import adam
import numpy as np
import pandas as pd

class mnistClassifier():
    
    def __init__(self, image_res = (28,28)):
        self.create_dense_model(image_res)

    def create_dense_model(self, image_res):
        
        model = Sequential()
        
        model.add(Conv2D(16, (3,3), strides = (2,2), activation='relu', input_shape = (*image_res,1)))
        model.add(Conv2D(32, (3,3), activation='relu'))
        model.add(Conv2D(32, (5,5), activation = 'relu'))
        model.add(Flatten())
        model.add(Dense(32, activation='relu'))
        model.add(Dense(10))
        model.add(Softmax())
        #model.compile(adam(), loss='categorical_crossentropy', metrics = 'accuracy')
        self.model = model

    def train_model(self, x_train, y_train, epochs = 10):
        self.model.compile(optimizer=adam(lr=0.001), loss = 'categorical_crossentropy', metrics = ['accuracy'])
        #expand dimensions and convert 
        x_train = np.expand_dims(x_train, -1)
        y_train_onehot = np.array(pd.get_dummies(pd.Categorical(y_train, categories = [0,1,2,3,4,5,6,7,8,9])))
        self.model.fit(x_train, y_train_onehot, batch_size=256, validation_split=0.2, epochs=epochs)
        
    def predict(self, x_test):
        x_test = np.expand_dims(x_test, -1)
        y_out = self.model.predict(x_test)
        return np.argmax(y_out, axis=1)
        
    def save_weights(self):
        self.model.save_weights('mnist_classifier.h5')
    
    def load_weights(self, file):
        self.model.load_weights(file)
        
        

if __name__ == '__main__':
    
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    image_res = x_train.shape[1::]
    classifier = mnistClassifier()
    classifier.train_model(x_train, y_train)
    classifier.save_weights()

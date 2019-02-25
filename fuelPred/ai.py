# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 13:33:49 2019

@author: s.granel
"""
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.models import load_model

class AI():
    def __init__(self, folder, filename):
        self.filename = filename
        self.folder = folder
        self.regressor = None
        
    def prepetualTraining(self, X_train, y_train):
        self.regressor = load_model(self.folder+self.filename)
        self.regressor.fit(X_train, y_train, batch_size=25, epochs=10)
        
    def save(self):
        self.regressor.save(self.folder + self.filename)
    
    def createLSTMOneReturn(self,num_hide_layers, num_units, X_train, y_train):
        self.regressor = Sequential()
        # Couche LSTM + Dropout
        self.regressor.add(LSTM(units=num_units, return_sequences=True, 
                           input_shape=(X_train.shape[1], X_train.shape[2])))
        self.regressor.add(Dropout(rate = 0.1))
        
        for layer in range(0, num_hide_layers):
            self.regressor.add(LSTM(units=num_units, return_sequences=True))
            self.regressor.add(Dropout(rate = 0.1))
        
        self.regressor.add(LSTM(units=num_units))
        self.regressor.add(Dropout(rate = 0.1))
        
        # Couche de sortie
        self.regressor.add(Dense(units=1))
        
        # Compilation
        self.regressor.compile(optimizer="adam", loss="mean_squared_error", metrics=['accuracy'])
        
        # Entrainer le réseau de neurones
        self.regressor.fit(X_train, y_train, batch_size=25, epochs=100)
    
    def createLSTMManyReturn(self,num_outputs, num_hide_layers, num_units, batch_size, num_epochs, X_train, y_train):
        self.regressor = Sequential()
        # Couche LSTM + Dropout
        self.regressor.add(LSTM(units=num_units, return_sequences=True, 
                           input_shape=(X_train.shape[1], X_train.shape[2])))
        self.regressor.add(Dropout(rate = 0.1))
        
        for layer in range(0, num_hide_layers):
            self.regressor.add(LSTM(units=num_units, return_sequences=True))
            self.regressor.add(Dropout(rate = 0.1))
        
        self.regressor.add(LSTM(units=num_units))
        self.regressor.add(Dropout(rate = 0.1))
        
        # Couche de sortie
        self.regressor.add(Dense(units=num_outputs))
        
        # Compilation
        self.regressor.compile(optimizer="adam", loss="categorical_crossentropy", metrics=['accuracy'])
        
        # Entrainer le réseau de neurones
        self.regressor.fit(X_train, y_train, batch_size=batch_size, epochs=num_epochs)
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 13:33:06 2019

@author: s.granel
"""

import numpy as np

class Data():
    def __init__(self, nb_predict):
        self.X_train = []
        self.y_train = []
        self.nb_pred_final = nb_predict
    
    def filledDataPetrol(self, training_set_scaled):  
        for i in range(self.nb_pred_final, len(training_set_scaled)) :
            self.X_train.append(training_set_scaled[(i - self.nb_pred_final):i, 0])
            self.y_train.append(training_set_scaled[i, 0])
        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)
        # Reshaping
        # On transforme X_train en un tableau à 3D pour l'entrée dans Karas et utilise 
        # aussi si on veut ajouter un nouveau tableau de paramètre (dans ce cas là, on ajoute de nouvelles dimensions)
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
        
    
    def filledDataFuel(self, training_set):
        
        nb_boucle = len(training_set)
        nb_depart = len(training_set) - 2000
        
        for i in range(nb_depart, nb_boucle) :
            self.y_train.append(training_set[i, 0])
        self.y_train = np.array(self.y_train)
        
        for variable in range(0,5):
            X = []
            for i in range(nb_depart, nb_boucle):
                X.append(training_set[i - self.nb_pred_final :i, variable])
            X = np.array(X)
            self.X_train.append(X)
        self.X_train = np.array(self.X_train)  
        self.X_train = np.swapaxes(np.swapaxes(self.X_train, 0, 1), 1, 2)
        
    def filledDataFuelPerpetual(self, training_set):
                
        self.y_train.append(training_set[len(training_set) - 1, 0])
        self.y_train = np.array(self.y_train)
        
        for variable in range(0,5):
            X = []
            X.append(training_set[0 : len(training_set)-1, variable])
            X = np.array(X)
            self.X_train.append(X)
        self.X_train = np.array(self.X_train)  
        self.X_train = np.swapaxes(np.swapaxes(self.X_train, 0, 1), 1, 2)
        
    def filledDataFuelDepAndPdv(self, training_set):
    
        self.X_train.append(training_set[0:len(training_set) - 1, 0])
        self.y_train.append(training_set[len(training_set) - 1, 0:4])
        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)
    
        # Reshaping
        # On transforme X_train en un tableau à 3D pour l'entrée dans Karas et utilise 
        # aussi si on veut ajouter un nouveau tableau de paramètre (dans ce cas là, on ajoute de nouvelles dimensions)
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
    
    def filledDataFuelDep(self, training_set):
        for i in range(self.nb_pred_final, len(training_set)-1) :
            self.X_train.append(training_set[(i - self.nb_pred_final):i, 0])
            self.y_train.append(training_set[i, 0:3])
        self.X_train = np.array(self.X_train)
        self.y_train = np.array(self.y_train)
                
        # Reshaping
        # On transforme X_train en un tableau à 3D pour l'entrée dans Karas et utilise 
        # aussi si on veut ajouter un nouveau tableau de paramètre (dans ce cas là, on ajoute de nouvelles dimensions)
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], self.X_train.shape[1], 1))
                
    def getXTrain(self):
        return self.X_train
    
    def getYTrain(self):
        return self.y_train
    
    
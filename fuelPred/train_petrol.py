# -*- coding: utf-8 -*-
"""
Created on Mon May 21 09:00:40 2018

@author: s.granel
"""

# Recurrent Neural Networks

# Partie 1 - Préparation des données
# Librairies
import sys
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from bdd import Bdd
from data import Data
from ai import AI

# Jeu d'entrainement
training_set = pd.DataFrame(columns=['A']);
folder = sys.argv[1]
#folder = ""

# Feature scaling
class Scale():
    def __init__(self, folder):
        self.filename = "scaler_predict_petrol.save"
        self.folder = folder
        self.sc = joblib.load(self.folder+ self.filename)
  
    def setScaledTraining(self, training_set):
        return self.sc.fit_transform(training_set)
    
    def save(self):
        joblib.dump(self.sc, self.folder + self.scaler_filename)

bdd = Bdd(True)
training_set = bdd.getTrainingSetPetrol(training_set)
training_set = np.flip(training_set,0)

scale = Scale(folder)

training_set_scaled = scale.setScaledTraining(training_set)

data = Data(110)
data.filledDataPetrol(training_set_scaled)

ai = AI(folder,'predict_petrol.h5')
ai.prepetualTraining(data.getXTrain(), data.getYTrain()) 
ai.save()
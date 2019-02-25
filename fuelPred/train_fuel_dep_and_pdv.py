# -*- coding: utf-8 -*-
"""
Created on Mon May 21 09:00:40 2018

@author: s.granel
"""

# Recurrent Neural Networks

# Partie 1 - Préparation des données
# Librairies
import pandas as pd
import numpy as np
import sys
from bdd import Bdd
from data import Data
from ai import AI

folder = sys.argv[1]
#folder = ""
filename = "predict_fuel_dep_and_pdv.h5"

idpdv = 33700023
idcarburant = 1

training_set = pd.DataFrame(columns=['A', 'B', 'C', 'D']);

bdd = Bdd(True)
training_set = bdd.filledTrainingSetFuelDepAndPdv(training_set, idpdv, idcarburant)
training_set = np.flip(training_set,0)

data = Data(400)
data.filledDataFuelDepAndPdv(training_set)

ai = AI(folder, filename)
ai.prepetualTraining(data.getXTrain(), data.getYTrain())
ai.save()
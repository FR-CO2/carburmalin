# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:02:50 2018

@author: s.granel
"""

#Imports
import pandas as pd
import numpy as np
import sys
from bdd import Bdd
from data import Data
from ai import AI

folder = sys.argv[1]
#folder = ""
filename = "predict_fuel_v2_400.h5"

idpdv = 33600001
idcarburant = 1
# Jeu d'entrainement
training_set = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E']);

bdd = Bdd(True)
training_set = bdd.getTrainingSetFuelV2(training_set, idpdv, idcarburant)
training_set = np.flip(training_set,0)

data = Data(400)
data.filledDataFuelPerpetual(training_set)

ai = AI(folder, filename)
ai.prepetualTraining(data.getXTrain(), data.getYTrain())
ai.save()

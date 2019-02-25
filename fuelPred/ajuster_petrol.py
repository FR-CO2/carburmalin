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
import psycopg2
import pprint

# Jeu d'entrainement
conn = None
training_set = pd.DataFrame(columns=['A']);
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT valeur from public.petrol_valeurs WHERE date > '2015-06-01' ORDER BY date ASC")
    rows = cur.fetchall()
    for record in rows:
        training_set =training_set.append({'A' :record[0]}, ignore_index=True)
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')

training_set = training_set[['A']].values    
# Feature scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0,1))
training_set_scaled = sc.fit_transform(training_set)

# Création de la structure avec 60 timesteps et 1 sortie
X_train = []
y_train = []
nb_pred_final = 75 # nombre de valeurs précédents celle-là
for i in range(nb_pred_final, len(training_set)-1) :
    X_train.append(training_set_scaled[(i-nb_pred_final):i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train = np.array(X_train)
y_train = np.array(y_train)


# Reshaping
# On transforme X_train en un tableau à 3D pour l'entrée dans Karas et utilise 
# aussi si on veut ajouter un nouveau tableau de paramètre (dans ce cas là, on ajoute de nouvelles dimensions)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
                      
# Partie 2 - Construction du RNN
# Librairies
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV

def build_classifier(optimizer):
    # Initialisation
    regressor = Sequential()
    
    # Couche LSTM + Dropout
    regressor.add(LSTM(units=50, return_sequences=True, 
                       input_shape=(X_train.shape[1], 1)))
    regressor.add(Dropout(rate = 0.1))
    
    # 2e couche LSTM + Dropout
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(rate = 0.1))
    
    # 3e couche LSTM + Dropout
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(rate = 0.1))
    
    # 4e couche LSTM + Dropout
    regressor.add(LSTM(units=50))
    regressor.add(Dropout(rate = 0.1))
    
    # Couche de sortie
    regressor.add(Dense(units=1))
    
    # Compilation
    regressor.compile(optimizer="adam", loss="mean_squared_error", metrics=['accuracy'])
    return regressor;

regressor = KerasClassifier(build_fn = build_classifier);
parameters= {"batch_size": [25,10],
             "epochs": [100,200],
             "optimizer":  ["adam"]}


grid_search = GridSearchCV(estimator=regressor, 
                            param_grid=parameters,
                            scoring="neg_mean_squared_error",
                            cv=10)
grid_search = grid_search.fit(X_train, y_train)

best_parameters = grid_search.best_params_
best_precision = grid_search.best_score_
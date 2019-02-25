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
from keras.models import load_model

iddep = '33%'
idcarburant = 1
# Jeu d'entrainement
conn = None
training_set = pd.DataFrame(columns=['A', 'B', 'C']);
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT min(val) as min_val, avg(val) as moy_val, max(val) as max_val from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE cast(pi.cp as text) like %s and idcarburant = %s GROUP BY date ORDER BY date ASC;", (iddep,idcarburant))
    rows = cur.fetchall()
    for record in rows:
        training_set = training_set.append({'A' :record[0], 'B' :record[1], 'C' : record[2]}, ignore_index=True)
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        print('Database connection closed.')
 
 
training_set = training_set[['A', 'B', 'C']].values  

# Feature scaling
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0,1))

X_train = []
y_train = []
nb_pred_final = 400 # nombre de valeurs précédents celle-là
for i in range(nb_pred_final, len(training_set)-1) :
    X_train.append(training_set[(i-nb_pred_final):i, 0])
    y_train.append(training_set[i, 0:3])
X_train = np.array(X_train)
y_train = np.array(y_train)


# Reshaping
# On transforme X_train en un tableau à 3D pour l'entrée dans Karas et utilise 
# aussi si on veut ajouter un nouveau tableau de paramètre (dans ce cas là, on ajoute de nouvelles dimensions)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
                      
# Partie 2 - Construction du RNN

folder = sys.argv[1]
#folder = ""
regressor = load_model(folder + 'predict_fuel_dep.h5')
# Entrainer le réseau de neurones
regressor.fit(X_train, y_train, batch_size=25, epochs=2)

# Sauvegarde de l'apprentissage
filename = 'predict_fuel_dep.h5'
regressor.save(folder + filename)
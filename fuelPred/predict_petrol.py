# -*- coding: utf-8 -*-
"""
Created on Mon May 21 09:08:37 2018

@author: s.granel
"""



# Deuxième partie : utilisation de notre RNN
# Chargement de l'apprentissage
import sys
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.externals import joblib
import psycopg2
import datetime

folder = sys.argv[1]
#folder = ""
model = load_model(folder+'predict_petrol.h5')
sc2 = joblib.load(folder+"scaler_predict_petrol.save")

# Jeu d'entrainement
conn = None
training_set = pd.DataFrame(columns=['A']);

date = datetime.date.today()
date = date - datetime.timedelta(130)
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT valeur from public.petrol_valeurs WHERE id in (select id from public.petrol_valeurs v2 where date >= %(date)s order by date desc limit 111) ORDER BY date ASC", {'date':date.isoformat()})
    rows = cur.fetchall()
    for record in rows:
        training_set =training_set.append({'A' :record[0]}, ignore_index=True)

    
    training_set = training_set[['A']].values   
    
    training_set_scaled = sc2.transform(training_set) 
    predicted = []
    
    def predict_petrol(training_set_scaled, model, predicted):
        
        # Création de la structure avec 60 timesteps et 1 sortie
        X_test = []
        nb_pred = 110
        nb_pred_final = len(training_set)-1 -nb_pred # nombre de valeurs précédents celle-là
        for i in range(nb_pred_final, len(training_set)-1) :
            X_test.append(training_set_scaled[i, 0])
            
        X_test =np.expand_dims(X_test, axis=1)
        X_test =np.expand_dims(X_test, axis=0)
        
        val = model.predict(X_test)
        training_set_scaled = np.delete(training_set_scaled, 0, 0)
        training_set_scaled = np.append(training_set_scaled, val[0])
        training_set_scaled =np.expand_dims(training_set_scaled, axis=1)
        return training_set_scaled
    
    for i in range(0,5):
        training_set_scaled = predict_petrol(training_set_scaled, model, predicted)
        predicted.append(training_set_scaled[110])
    
    predicted = sc2.inverse_transform(predicted)
    date_batch = datetime.date.today()
    date_predict = date_batch
    
    for i in range(0,5):
        date_predict = date_predict + datetime.timedelta(1)
        cur.execute("SELECT valeur from public.predict_petrol_valeurs WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s ", {'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat()})
        rows = cur.fetchall()
        result = 0
        for record in rows:
            result = 1
        if(result == 0):
            cur.execute("INSERT INTO public.predict_petrol_valeurs (valeur, date_predict, date_batch) VALUES(%(val)s, %(date_predict)s, %(date_batch)s)", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat()})
        else :
            cur.execute("UPDATE public.predict_petrol_valeurs SET valeur = %(val)s  WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat()})
        conn.commit()
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        #print('Database connection closed.')

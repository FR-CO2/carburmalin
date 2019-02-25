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
from sklearn.externals import joblib
import datetime

date = datetime.date.today()
date = date + datetime.timedelta(-401)

folder = sys.argv[1]
#folder = ""
list_element = sys.argv[2]
#list_element = "61:1;61:2;61:3;61:4;61:5;61:6"

elements = list_element.split(";")

model = load_model(folder+'predict_fuel_dep.h5')
sc2 = joblib.load(folder+"predict_fuel_dep.save")

#idcarburant = 1
# Jeu d'entrainement
conn = None
iddep = None
iddepLike = None
idcarburant = None
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    
    for ele in elements : 
        ids = ele.split(":")
        iddep = ids[0]
        iddepLike = iddep+'%'
        idcarburant = ids[1]

        training_set = pd.DataFrame(columns=['A', 'B', 'C']);
        cur.execute("SELECT min(val) as min_val, max(val) as max_val, avg(val) as moy_val, date from public.pdv_valeurs pv WHERE idpdv in (SELECT idpdv FROM pdv_infos pi WHERE cast(pi.cp as text) like %(dep)s) and idcarburant = %(idcarburant)s GROUP BY pv.date ORDER BY pv.date DESC LIMIT 401;", {'dep' :iddepLike, 'idcarburant' : idcarburant})
        rows = cur.fetchall()
        for record in rows:
            training_set = training_set.append({'A' :record[0], 'B' :record[1], 'C' : record[2]}, ignore_index=True)   
         
        training_set = training_set[['A', 'B', 'C']].values  
             
        predicted = []
        
        def predict_dep(training_set, model, predicted):
            
            # Création de la structure avec 60 timesteps et 1 sortie
            X_test = []
            nb_pred = 400
            nb_pred_final = len(training_set)-1-nb_pred # nombre de valeurs précédents celle-là
            if(nb_pred_final < 0):
                return
            
            for i in range(nb_pred_final, len(training_set)-1) :
                X_test.append(training_set[i, 0])
                
            X_test =np.expand_dims(X_test, axis=1)
            X_test =np.expand_dims(X_test, axis=0)
            
            val = model.predict(X_test)
            temp = val[0][0]
            val[0][0] = val[0][2]
            val[0][2] = temp
            training_set = np.delete(training_set, 0, 0)
            training_set = np.append(training_set, val,axis=0)
            return training_set
        
        for i in range(0,5):
            training_set = predict_dep(training_set, model, predicted)
            if(training_set is None):
                training_set = []
            else :
                predicted.append(training_set[400])
        
        date_batch = datetime.date.today()
        date_predict = date_batch
       
        if len(predicted) > 4:
            for i in range(0,5):
                cur.execute("SELECT valeur_min, valeur_max, valeur_avg from public.predict_fuel_dep_valeurs WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and dep = %(dep)s and idcarburant = %(idcarburant)s", {'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'dep' : iddep, 'idcarburant' : idcarburant})
                rows = cur.fetchall()
                result = 0
                for record in rows:
                    result = 1
                if(result == 0):
                    cur.execute("INSERT INTO public.predict_fuel_dep_valeurs (valeur_min, valeur_avg, valeur_max, date_predict, date_batch, dep, idcarburant) VALUES(%(val_min)s, %(val_avg)s, %(val_max)s, %(date_predict)s, %(date_batch)s, %(iddep)s, %(idcarburant)s)", {'val_min' : predicted[i][0], 'val_avg' : predicted[i][1], 'val_max' : predicted[i][2] ,'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'iddep' : iddep, 'idcarburant' : idcarburant})
                else :
                    cur.execute("UPDATE public.predict_fuel_dep_valeurs SET valeur_min = %(val_min)s, valeur_avg = %(val_avg)s, valeur_max = %(val_max)s WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and dep = %(iddep)s and idcarburant = %(idcarburant)s", {'val_min' : predicted[i][0], 'val_avg' : predicted[i][1], 'val_max' : predicted[i][2], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'iddep' : iddep, 'idcarburant' : idcarburant})
                conn.commit()
                date_predict = date_predict + datetime.timedelta(1)
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        #print('Database connection closed.')

# -*- coding: utf-8 -*-
"""
Created on Mon May 21 08:59:37 2018

@author: s.granel
"""

#Imports
import sys
import numpy as np
import pandas as pd
import psycopg2
from keras.models import load_model
import datetime

folder = sys.argv[1]
#folder = ""
idpdv = sys.argv[2]
#idpdv = 33600001
idcarburant = sys.argv[3]
#print(idpdv)
#print(idcarburant)
idcarburant = 1
# Jeu d'entrainement
conn = None
training_set = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E']);
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT val,date, substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE id in (select id from public.pdv_valeurs pv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date DESC LIMIT 401) ORDER BY date ASC;", (idpdv,idcarburant))
    rows = cur.fetchall()
    for record in rows:
        cur.execute("SELECT valeur from public.petrol_valeurs WHERE date <= %s ORDER BY date DESC LIMIT 1", (record[1],))
        row = cur.fetchone()
        cur.execute("SELECT min(val), avg(val), max(val) from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE date = %s AND length(cast(cp as varchar)) = 5 and substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) = %s and idcarburant = %s", (record[1],record[2], 1))
        vals = cur.fetchone()
        training_set = training_set.append({'A' :record[0], 'B' :row[0], 'C' : vals[0], 'D' :vals[1], 'E' : vals[2]}, ignore_index=True)
     
    training_set = training_set[['A', 'B', 'C', 'D', 'E']].values 
    
    model = load_model(folder + 'predict_fuel_v2_400.h5')
    
    #On met le tout dans des vecteurs qui seront donnés à Keras
    #Remarque : il faut de la mémoire sur votre ordinateur
    #On initialise les vecteurs
    # Création de la structure avec 60 timesteps et 1 sortie
    
    predicted = []
    
    def predict_petrol(training_set, model, predicted,date):
        
        # Création de la structure avec 60 timesteps et 1 sortie
        X_test = []
    
        nb_pred = 400
        nb_pred_final = len(training_set)-1-nb_pred # nombre de valeurs précédents celle-là
        nb_boucle = len(training_set)-1
        
        for variable in range(0,5):
            X = []
            for i in range(nb_pred_final, nb_boucle):
                X.append(training_set[i:i+1, variable])
            X = np.array(X)
            X_test.append(X)
        X_test = np.array(X_test)  
        X_test = np.swapaxes(X_test, 0, 2)
        
        val = model.predict(X_test)
        training_set = np.delete(training_set, 0, 0)
        vals = val
        vals = getValsAlreadyPredicted(vals, date)
        vals = np.expand_dims(vals, axis=1)
        vals = np.swapaxes(vals, 0, 1)
    
        training_set = np.append(training_set, vals,axis=0)
        return training_set
    
    def getValsAlreadyPredicted(vals, date):
        date_batch = datetime.date.today()
        
        training_set_predict_petrol = pd.DataFrame(columns=['A']);
        if(date == date_batch):
            #Connexion à la bdd
            cur.execute("SELECT valeur from public.petrol_valeurs WHERE date = %(date)s", {'date' : date.isoformat()})
            row = cur.fetchone()
            training_set_predict_petrol = training_set_predict_petrol.append({'A' :row[0]}, ignore_index=True)
         
        else :
            #Connexion à la bdd
            cur.execute("SELECT valeur from public.predict_petrol_valeurs WHERE date_predict = %(date_predict)s AND date_batch = %(date_batch)s ", {'date_predict' : date.isoformat(),'date_batch' : date_batch.isoformat()})
            row = cur.fetchone()
            training_set_predict_petrol = training_set_predict_petrol.append({'A' :row[0]}, ignore_index=True)
          
        training_set_predict_petrol = training_set_predict_petrol[['A']].values 
        vals = np.append(vals, training_set_predict_petrol)
    
        training_set_predict_fuel_dep = pd.DataFrame(columns=['A', 'B', 'C']);
        #Connexion à la bdd
        
        cur.execute("SELECT valeur_min, valeur_avg, valeur_max from public.predict_fuel_dep_valeurs WHERE date_predict = %(date_predict)s AND dep = %(dep)s AND date_batch = %(date_batch)s " , {'date_predict' : date.isoformat(), 'dep': 33, 'date_batch' : date_batch.isoformat()})
        row = cur.fetchone()
        training_set_predict_fuel_dep = training_set_predict_fuel_dep.append({'A' :row[0], 'B' :row[1], 'C' :row[2]}, ignore_index=True)
       
        vals = np.append(vals, training_set_predict_fuel_dep)
        return vals
    
    date_batch = datetime.date.today()
    date_predict = date_batch
    for i in range(0,5):
        training_set = predict_petrol(training_set, model, predicted,date_predict)
        predicted.append(training_set[400])
        date_predict = date_predict + datetime.timedelta(1)
    
    date_batch = datetime.date.today()
    date_predict = date_batch
       
    for i in range(0,5):
        cur.execute("SELECT valeur from public.predict_fuel_valeurs WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
        rows = cur.fetchall()
        result = 0
        for record in rows:
            result = 1
        if(result == 0):
            cur.execute("INSERT INTO public.predict_fuel_valeurs (valeur, date_predict, date_batch, idpdv, idcarburant) VALUES(%(val)s, %(date_predict)s, %(date_batch)s, %(idpdv)s, %(idcarburant)s)", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
        else :
            cur.execute("UPDATE public.predict_fuel_valeurs SET valeur = %(val)s WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
        conn.commit()
        date_predict = date_predict + datetime.timedelta(1)
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        #print('Database connection closed.')

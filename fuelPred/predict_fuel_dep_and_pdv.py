# -*- coding: utf-8 -*-
"""
Created on Mon May 21 09:00:40 2018

@author: s.granel
"""

#Imports
import sys
import numpy as np
import pandas as pd
import psycopg2
from keras.models import load_model
import datetime
import time

folder = sys.argv[1]
#folder = ""
list_element = sys.argv[2]
#list_element = "33600006:1;33600006:2;33600006:3;33600006:4;33600006:5;33600006:6"
#idcarburant = 1
model = load_model(folder+'predict_fuel_dep_and_pdv.h5')
# Jeu d'entrainement
conn = None

elements = list_element.split(";")

connVPS = None
idpdv = None
idcarburant = None
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()

    connVPS = psycopg2.connect("dbname='fuelpred' user='postgres' host='51.75.207.51' password='j9lk_hQb'")
    curVPS = connVPS.cursor()
    

    for ele in elements : 
        ids = ele.split(":")
        idpdv = ids[0]
        idcarburant = ids[1]
        tmps1 = time.time()
        training_set = pd.DataFrame(columns=['A', 'B', 'C', 'D']);
        
        cur.execute("SELECT val,date, substring(cp, 1, char_length(cp)-3) as cp From public.pdv_valeurs pv1 INNER JOIN pdv_infos pi ON pv1.idpdv = pi.idpdv WHERE pv1.id in( SELECT pv.id from public.pdv_valeurs pv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date desc limit 401) ORDER BY date ASC;", (idpdv,idcarburant))
        rows = cur.fetchall()
        if(len(rows) < 400) : 
            #print("KO : " +idpdv + ","+ idcarburant + " : " + str(len(rows)))
            continue
        for record in rows:
            cur.execute("SELECT min(val), avg(val), max(val) from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE date = %s AND length(cast(cp as varchar)) = 5 and substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) = %s and idcarburant = %s", (record[1],record[2], 1))
            vals = cur.fetchone()
            training_set = training_set.append({'A' :record[0], 'B' : vals[0], 'C' :vals[1], 'D' : vals[2]}, ignore_index=True)
             
        training_set = training_set[['A', 'B', 'C', 'D']].values    
         
        predicted = []
        
        def predict_dep(training_set, model, predicted):
            
            # Création de la structure avec 400 timesteps et 1 sortie
            X_test = []
            nb_pred = 400
            nb_pred_final = len(training_set)-1 -nb_pred # nombre de valeurs précédents celle-là
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
                curVPS.execute("SELECT valeur_pdv, valeur_min, valeur_max, valeur_avg from public.predict_fuel_dep_pdv_valeurs WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                rows = curVPS.fetchall()
                result = 0
                for record in rows:
                    result = 1
                if(result == 0):
                    curVPS.execute("INSERT INTO public.predict_fuel_dep_pdv_valeurs (valeur_pdv, valeur_min, valeur_avg, valeur_max, date_predict, date_batch, idpdv, idcarburant) VALUES(%(val_pdv)s, %(val_min)s, %(val_avg)s, %(val_max)s, %(date_predict)s, %(date_batch)s, %(idpdv)s, %(idcarburant)s)", {'val_pdv' : predicted[i][0], 'val_min' : predicted[i][1], 'val_avg' : predicted[i][2], 'val_max' : predicted[i][3] ,'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                else :
                    curVPS.execute("UPDATE public.predict_fuel_dep_pdv_valeurs SET valeur_pdv = %(val_pdv)s, valeur_min = %(val_min)s, valeur_avg = %(val_avg)s, valeur_max = %(val_max)s WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'val_pdv' : predicted[i][0], 'val_min' : predicted[i][1], 'val_avg' : predicted[i][2], 'val_max' : predicted[i][3], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                connVPS.commit()
                date_predict = date_predict + datetime.timedelta(1)
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
        #print('Database connection closed.')

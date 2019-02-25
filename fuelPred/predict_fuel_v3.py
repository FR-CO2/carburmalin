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
import time

folder = sys.argv[1]
#folder = ""
list_element = sys.argv[2]
#list_element = "67000027:6;76680004:6;77550005:4;92370002:5;95320006:1;59300016:1;9100006:1;6160007:1;26270005:4;33480003:2;58000011:6;62300014:1;34110005:6;35290003:2;59110006:6;59750005:6;37700011:1;15200001:1;77190005:4;92230011:5;63170007:1;76550001:1;94380004:5;14123008:5;59510003:6;82270002:4;95650002:4;67640005:3;25620001:6;37270006:1;91400010:4;31150005:5;81500001:6;91300020:6;48300006:5;71700006:6;69570005:5;91170006:5;22810002:6;35800004:5;42000014:1;94003002:6;88000009:3;62320001:6;28000011:4;1430003:6;5100008:6;94370008:5;73300002:1;24120007:4;93230005:5;13200015:4;33290009:6;37110004:6;71100027:6;33370015:1;91450001:6;6320006:1;51700001:2;93120004:6;77150003:2;78310006:1;77350005:1;62170005:1;64140004:2;60200012:1;67260007:4;81500001:4;77130011:1;39140006:6;1960004:5;30900017:1;27210007:5;89100014:5;25640007:4;14600007:6;13110005:3;59146002:6;54600005:1;93400010:6;6600023:6;92000020:1;71250007:1;78520004:1;75020010:5;83380002:1;13220003:6;25000023:6;37160003:2;16190001:1;42110006:5;27000008:1;78400004:1;78480004:5;94550002:6;65100009:5;69360015:6;75019016:5;91190011:1;30130010:5;40100008:5;71100027:5;78210006:6;93400011:1;38640001:2;69310004:5;59000019:6;35310004:1;73420005:1;73100012:6;34070016:6;15000016:5;6800020:6;89470004:6;13011016:4;49300009:2;54200012:6;28000009:5;32600001:1;64320005:6;33700023:4;59110005:6;94380004:1;95712003:5;31340001:1;33720008:4;76420006:5;79800011:4;6600024:1;64600007:3;60000012:1;64140005:6;33840003:1;64170010:5;34070017:5;31120010:4;78980001:1;54300011:6;64400005:1;13090017:3;44300016:1;83230006:1;51200006:5;46000012:6;71400013:5;80330004:6;47310006:4;62250010:1;62250010:5;76140001:2;21230004:1;64000016:6;35760004:6;60700004:5;91940008:1;82400003:1;36350002:5;51200006:1;52000009:3;93500008:1;68390004:4;14000019:6;62170005:6;33780001:1;33700022:3;76000006:6;10600009:5;63000022:1;33600009:4;80590002:1;95470005:3;17350001:1;59210005:5;75013022:5;88450002:6;37100011:6;69800017:1;76120008:1;80270001:1;68300004:5;69190009:6;77950001:2;37170006:6;62250011:1;88400005:1;60500011:6;41000019:4;77000013:1;27210007:4;34250003:1;78760004:1;84300011:4;51300014:6;13500011:6;31770005:1;31290008:6;21240004:6;45430006:6;13013016:1;35510005:1"
#list_element= "21160004:6"
model = load_model(folder + 'predict_fuel_v2_400.h5')

elements = list_element.split(";")

conn = None
connVPS= None
idpdv = None
idcarburant = None
dep = None
date_predict = None

try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    
    connVPS = psycopg2.connect("dbname='fuelpred' user='postgres' host='51.75.207.51' password='j9lk_hQb'")
    curVPS = connVPS.cursor()
    

    for ele in elements : 
        ids = ele.split(":")
        idpdv = ids[0]
        idcarburant = ids[1]
        dep = idpdv[:2]
        tmps1 = time.time()
        # Jeu d'entrainement
        training_set = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E']);
        #Connexion à la bdd
        
        cur.execute("SELECT val,date, substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE id in (select id from public.pdv_valeurs pv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date DESC LIMIT 401) ORDER BY date ASC;", (idpdv,idcarburant))
        rows = cur.fetchall()
        if(len(rows) < 400) : 
            continue
        for record in rows:
            cur.execute("SELECT valeur from public.petrol_valeurs WHERE date <= %s ORDER BY date DESC LIMIT 1", (record[1],))
            row = cur.fetchone()
            cur.execute("SELECT min(val), avg(val), max(val) from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE date = %s AND length(cast(cp as varchar)) = 5 and substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) = %s and idcarburant = %s", (record[1],record[2], 1))
            vals = cur.fetchone()
            training_set = training_set.append({'A' :record[0], 'B' :row[0], 'C' : vals[0], 'D' :vals[1], 'E' : vals[2]}, ignore_index=True)
         
        training_set = training_set[['A', 'B', 'C', 'D', 'E']].values 
        
               
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
            if(nb_pred_final < 0):
                return
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
                cur.execute("SELECT valeur from public.petrol_valeurs WHERE date = %(date)s LIMIT 1", {'date' : date.isoformat()})
                row = cur.fetchone()
                training_set_predict_petrol = training_set_predict_petrol.append({'A' :row[0]}, ignore_index=True)
             
            else :
                #Connexion à la bdd
                cur.execute("SELECT valeur from public.predict_petrol_valeurs WHERE date_predict = %(date_predict)s AND date_batch = %(date_batch)s LIMIT 1", {'date_predict' : date.isoformat(),'date_batch' : date_batch.isoformat()})
                row = cur.fetchone()
                training_set_predict_petrol = training_set_predict_petrol.append({'A' :row[0]}, ignore_index=True)
              
            training_set_predict_petrol = training_set_predict_petrol[['A']].values 
            vals = np.append(vals, training_set_predict_petrol)
        
            training_set_predict_fuel_dep = pd.DataFrame(columns=['A', 'B', 'C']);
            #Connexion à la bdd
            
            cur.execute("SELECT valeur_min, valeur_avg, valeur_max from public.predict_fuel_dep_valeurs WHERE date_predict = %(date_predict)s AND dep = %(dep)s AND date_batch = %(date_batch)s and idcarburant = %(idcarburant)s LIMIT 1" , {'date_predict' : date.isoformat(), 'dep': dep, 'date_batch' : date_batch.isoformat(), 'idcarburant' : idcarburant})
            row = cur.fetchone()
            training_set_predict_fuel_dep = training_set_predict_fuel_dep.append({'A' :row[0], 'B' :row[1], 'C' :row[2]}, ignore_index=True)
           
            vals = np.append(vals, training_set_predict_fuel_dep)
            return vals
        
        date_batch = datetime.date.today()
        date_predict = date_batch
        for i in range(0,5):
            training_set = predict_petrol(training_set, model, predicted,date_predict)
            if(training_set is None):
                training_set = []
            else :
                predicted.append(training_set[400])
                date_predict = date_predict + datetime.timedelta(1)
        
        date_batch = datetime.date.today()
        date_predict = date_batch
        
        if len(predicted) > 4:
            for i in range(0,5):
                curVPS.execute("SELECT valeur from public.predict_fuel_valeurs WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                rows = curVPS.fetchall()
                result = 0
                for record in rows:
                    result = 1
                if(result == 0):
                    curVPS.execute("INSERT INTO public.predict_fuel_valeurs (valeur, date_predict, date_batch, idpdv, idcarburant) VALUES(%(val)s, %(date_predict)s, %(date_batch)s, %(idpdv)s, %(idcarburant)s)", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                else :
                    curVPS.execute("UPDATE public.predict_fuel_valeurs SET valeur = %(val)s WHERE date_predict = %(date_predict)s and date_batch = %(date_batch)s and idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'val' : predicted[i][0], 'date_predict' : date_predict.isoformat(), 'date_batch' : date_batch.isoformat(), 'idpdv' : idpdv, 'idcarburant' : idcarburant})
                connVPS.commit()
                date_predict = date_predict + datetime.timedelta(1)
            tmps2 = time.time() - tmps1
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
        #print('Database connection closed.')

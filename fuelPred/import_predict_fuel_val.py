# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 10:26:07 2018

@author: s.granel
"""
import psycopg2
import sys

date = sys.argv[1]

# Jeu d'entrainement
conn = None
connVps = None
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    
    connVPS = psycopg2.connect("dbname='fuelpred' user='postgres' host='51.75.207.51' password='j9lk_hQb'")
    curVPS = connVPS.cursor()
    
    curVPS.execute("SELECT id, idpdv, valeur, idcarburant, date_predict, date_batch from public.predict_fuel_valeurs WHERE date_batch = %(date)s order by date_batch desc", {'date' : date})
    
    rows = curVPS.fetchall()
    cpt = 1
    for record in rows:
        print(str(cpt))
        
        cur.execute("SELECT valeur from public.predict_fuel_valeurs WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s AND date_predict = %(date_predict)s and date_batch = %(date_batch)s ", {'idpdv' : record[1], 'idcarburant' : record[3], 'date_predict' : record[4], 'date_batch' : record[5]})
        rows = cur.fetchall()
        resultVPS = 0
        for recordVPS in rows:
            resultVPS = 1
        if(resultVPS == 0):
            cur.execute("INSERT INTO public.predict_fuel_valeurs (idpdv, idcarburant, valeur, date_predict, date_batch) VALUES(%(idpdv)s,%(idcarburant)s,%(val)s, %(date_predict)s, %(date_batch)s)", {'idpdv' : record[1], 'idcarburant' : record[3], 'val' : record[2], 'date_predict' : record[4], 'date_batch' : record[5]})
            print('Insert : idpdv : ' +str(record[1])+' idcarburant : ' + str(record[3]) + ' date_predict : ' +str(record[4])+' date_batch : '+str(record[5]))
        conn.commit()
        cpt = cpt +1
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
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
    
    curVPS.execute("SELECT valeur_pdv, valeur_min, date_predict, date_batch, valeur_max, valeur_avg, idcarburant, idpdv from public.predict_fuel_dep_pdv_valeurs where date_batch = %(date)s order by date_batch desc", {'date' : date})
    
    rows = curVPS.fetchall()
    cpt = 1;
    for record in rows:
        print(str(cpt))
        cur.execute("SELECT valeur_pdv from public.predict_fuel_dep_pdv_valeurs WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s AND date_predict = %(date_predict)s and date_batch = %(date_batch)s ", {'idpdv' : record[7], 'idcarburant' : record[6], 'date_predict' : record[2], 'date_batch' : record[3]})
        rows = cur.fetchall()
        resultVPS = 0
        for recordVPS in rows:
            resultVPS = 1
        if(resultVPS == 0):
            cur.execute("INSERT INTO public.predict_fuel_dep_pdv_valeurs (valeur_pdv, valeur_min, date_predict, date_batch, valeur_max, valeur_avg, idcarburant, idpdv) VALUES(%(valeur_pdv)s,%(valeur_min)s,%(date_predict)s, %(date_batch)s, %(valeur_max)s, %(valeur_avg)s, %(idcarburant)s, %(idpdv)s)", {'valeur_pdv' : record[0], 'valeur_min' : record[1], 'date_predict' : record[2], 'date_batch' : record[3], 'valeur_max' : record[4], 'valeur_avg' : record[5], 'idcarburant' :record[6], 'idpdv' : record[7]})
            print('Insert')
        conn.commit()
        cpt = cpt +1
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
        #print('Database connection closed.')

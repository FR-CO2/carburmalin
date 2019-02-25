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
connVPS = None
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT idpdv, idcarburant, date_batch, predict_petrol, predict_wo_petrol FROM public.stat WHERE date_batch = %(date)s order by date_batch desc", {'date' : date})
    
    connVPS = psycopg2.connect("dbname='fuelpred' user='postgres' host='51.75.207.51' password='j9lk_hQb'")
    curVPS = connVPS.cursor()
    rows = cur.fetchall()
    cpt = 1
    for record in rows:
        print(str(cpt))
        
        curVPS.execute("SELECT idpdv from public.stat WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s and date_batch = %(date_batch)s ", {'idpdv' : record[0], 'idcarburant' : record[1],  'date_batch' : record[2]})
        rowsVPS = curVPS.fetchall()
        resultVPS = 0
        for recordVPS in rowsVPS:
            resultVPS = 1
        if(resultVPS == 0):
            curVPS.execute("INSERT INTO public.stat (idpdv, idcarburant, date_batch, predict_petrol, predict_wo_petrol) VALUES(%(idpdv)s,%(idcarburant)s, %(date_batch)s, %(predict_petrol)s, %(predict_wo_petrol)s)", {'idpdv' : record[0], 'idcarburant': record[1], 'date_batch' : record[2], 'predict_petrol' : record[3], 'predict_wo_petrol' : record[4]})
            print('Insert : idpdv : ' +str(record[0])+' idcarburant : ' + str(record[1]) + ' date_predict : ' +str(record[2]))
        cpt = cpt +1
    connVPS.commit()
        
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
        #print('Database connection closed.')

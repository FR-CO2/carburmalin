# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 10:26:07 2018

@author: s.granel
"""
import psycopg2
import sys

date = sys.argv[1]
#date = '2018-12-13'

# Jeu d'entrainement
conn = None
connVPS = None
idpdv = None
idcarburant = None
#Connexion à la bdd
try:
    conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
    cur = conn.cursor()
    cur.execute("SELECT idpdv, idcarburant FROM public.pdv_valeurs WHERE date = %(date)s GROUP by idpdv, idcarburant", {'date' : date})
    
    connVPS = psycopg2.connect("dbname='fuelpred' user='postgres' host='51.75.207.51' password='j9lk_hQb'")
    curVPS = connVPS.cursor()
    rows = cur.fetchall()
    cpt = 1
    for record in rows:
        print(str(cpt))
        idpdv = record[0]
        idcarburant = record[1]
        cur.execute("SELECT date FROM public.pdv_valeurs WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s and date = %(date)s ORDER BY date DESC LIMIT 1", {'idpdv' : record[0], 'idcarburant' : record[1], 'date' : date})
        rowDate = cur.fetchone()
        
        cur.execute("SELECT Count(idpdv) as cpt FROM public.pdv_valeurs WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s GROUP BY idpdv, idcarburant", {'idpdv' : record[0], 'idcarburant' : record[1]})
        rowNbVal = cur.fetchone()
        
        curVPS.execute("SELECT date from public.pdv_val_last_update WHERE idpdv = %(idpdv)s and idcarburant = %(idcarburant)s", {'idpdv' : record[0], 'idcarburant' : record[1]})
        rowsVPS = curVPS.fetchall();
        resultVPS = 0
        for recordVPS in rowsVPS:
            resultVPS = 1
        if(resultVPS == 0):
            curVPS.execute("INSERT INTO public.pdv_val_last_update (idpdv, idcarburant, date, nbval) VALUES(%(idpdv)s,%(idcarburant)s, %(date)s, %(nbval)s)", {'idpdv' : record[0], 'idcarburant': record[1], 'date' : rowDate, 'nbval' : rowNbVal})
            print('Insert : idpdv : ' +str(record[0])+' idcarburant : ' + str(record[1]) + ' date : ' +str(rowDate))
        else:
            curVPS.execute("update public.pdv_val_last_update set date = %(date)s, nbval = %(nbval)s WHERE idpdv =%(idpdv)s and idcarburant = %(idcarburant)s", {'idpdv' : record[0], 'idcarburant': record[1], 'date' : rowDate, 'nbval' : rowNbVal})
            print('Update : idpdv : ' +str(record[0])+' idcarburant : ' + str(record[1]) + ' date : ' +str(rowDate))
        cpt = cpt +1
        connVPS.commit()
        
except:
    print("I am unable to connect to the database.")
finally:
    if conn is not None:
        conn.close()
        connVPS.close()
        #print('Database connection closed.')

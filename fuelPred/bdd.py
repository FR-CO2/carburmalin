# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 13:22:06 2019

@author: s.granel
"""
import psycopg2

class Bdd():
    
    def __init__(self,perpetual_training):
        self.conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
        self.error_msg = "I am unable to connect to the database."
        self.final_msg = 'Database connection closed.'
        self.perpetual_training = perpetual_training
    
    def getTrainingSetPetrol(self, training_set):
        #Connexion à la bdd
        try:
            cur = self.conn.cursor()
            request = "SELECT valeur from public.petrol_valeurs WHERE date > '2017-01-01' ORDER BY date ASC"
            if self.perpetual_training == True:
                request = "SELECT valeur from public.petrol_valeurs WHERE date > '2017-01-01' ORDER BY date DESC Limit 111"
            cur.execute(request)
            rows = cur.fetchall()
            for record in rows:
                training_set =training_set.append({'A' :record[0]}, ignore_index=True)
            return training_set[['A']].values
        except:
            print(self.error_msg)
        finally:
            if self.conn is not None:
                self.conn.close()
                print(self.final_msg)

    def getTrainingSetFuelV2(self, training_set, idpdv, idcarburant):
        try:
            conn = psycopg2.connect("dbname='fuelpred' user='fuelpred' host='localhost' password='fuelpred'")
            cur = conn.cursor()
            request = "SELECT val,date, substring(cp, 1, char_length(cp)-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date ASC;"
            if self.perpetual_training == True:
                request = "SELECT val,date, substring(cp, 1, char_length(cp)-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date DESC LIMIT 401;"
            cur.execute(request, (idpdv,idcarburant))
            rows = cur.fetchall()
            for record in rows:
                cur.execute("SELECT valeur from public.petrol_valeurs WHERE date <= %s ORDER BY date DESC LIMIT 1", (record[1],))
                row = cur.fetchone()
                cur.execute("SELECT min(val), avg(val), max(val) from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE date = %s AND length(cast(cp as varchar)) = 5 and substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) = %s and idcarburant = %s", (record[1],record[2], 1))
                vals = cur.fetchone()
                training_set = training_set.append({'A' :record[0], 'B' :row[0], 'C' : vals[0], 'D' :vals[1], 'E' : vals[2]}, ignore_index=True)
            return training_set[['A', 'B', 'C', 'D', 'E']].values 
        except:
            print(self.error_msg)
        finally:
            if self.conn is not None:
                self.conn.close()
                print(self.final_msg)

         
    def filledTrainingSetFuelDepAndPdv(self, training_set, idpdv, idcarburant):
        
        #Connexion à la bdd
        try:
            cur = self.conn.cursor()
            request = "SELECT val,date, substring(cp, 1, char_length(cp)-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date ASC;"
            if self.perpetual_training == True:
                request = "SELECT val,date, substring(cp, 1, char_length(cp)-3) as cp  from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE pv.idpdv = %s and idcarburant = %s ORDER BY date DESC limit 401;"
            cur.execute(request, (idpdv,idcarburant))
            rows = cur.fetchall()
            for record in rows:
                cur.execute("SELECT min(val), avg(val), max(val) from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE date = %s AND length(cast(cp as varchar)) = 5 and substring(cast(cp as varchar), 1, char_length(cast(cp as varchar))-3) = %s and idcarburant = %s", (record[1],record[2], 1))
                vals = cur.fetchone()
                training_set = training_set.append({'A' :record[0], 'B' : vals[0], 'C' :vals[1], 'D' : vals[2]}, ignore_index=True)
            return training_set[['A', 'B', 'C', 'D']].values  
        except:
            print(self.error_msg)
        finally:
            if self.conn is not None:
                self.conn.close()
                print(self.final_msg)
                
    def filledTrainingSetFuelDep(self, training_set, iddep, idcarburant):
        
        #Connexion à la bdd
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT min(val) as min_val, avg(val) as moy_val, max(val) as max_val from public.pdv_valeurs pv INNER JOIN pdv_infos pi ON pv.idpdv = pi.idpdv WHERE cast(pi.cp as text) like %s and idcarburant = %s GROUP BY date ORDER BY date ASC;", (iddep,idcarburant))
            rows = cur.fetchall()
            for record in rows:
                training_set = training_set.append({'A' :record[0], 'B' :record[1], 'C' : record[2]}, ignore_index=True)
            return training_set[['A', 'B', 'C']].values  
        except:
            print(self.error_msg)
        finally:
            if self.conn is not None:
                self.conn.close()
                print(self.final_msg)
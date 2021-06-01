# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:48:41 2021

@author: Polonius

Script for calibration measurments - experiment done in 1D setup, where exact
distance between smartphone and beacon was known.

Searched values:
n - enviromental constant
TxPower - RSSI of beacon on the 1m distance
"""

import sqlite3
import numpy as np
import math
from os import path
from matplotlib import pyplot as plt

def openDataBase(dbName):
    if not path.exists(dbName): #Create database if not existing
        con=sqlite3.connect(dbName)
        con.execute("""CREATE TABLE beacons(name TEXT, x INTEGER, y INTEGER, z INTEGER);""")
        con.commit()
        con.execute("""CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, mac TEXT);""")
        con.commit()
        print("Data base created!\n")
    else:
        con=sqlite3.connect(dbName)
        print("Data base finded!\n")
        
    return con

def importUser(con,userID):
    tableName='user'+userID
    cursor=con.execute("SELECT * FROM "+tableName)
    rows=cursor.fetchall()
    contactList=[]
    for row in rows:
        contactList.append((row[0],row[1].replace('\r\n',''),row[2]))
    return contactList
    
con=openDataBase('locBT_test_calibration.db')
data=importUser(con,'1')

#Remove the same rows
data=data[0:len(data):2]

rssi=[int(contact[2][0:-3]) for contact in data]
x=[10*(len(rssi)-x-1) for x in range(len(rssi))]

plot=plt.figure(0)
plt.plot(x,rssi,marker='o',linestyle='', label="Eksperyment")
plt.xlabel('Odległosć [cm]'), plt.ylabel('Moc [dBm]')

y=[10*math.log10(x1) for x1 in x[:-1]]

coeff,cov=np.polyfit([-1*rssi1 for rssi1 in rssi[:-1]],y,1,cov=True)

a=coeff[0]
b=coeff[1]

ua=cov[0][0]
ub=cov[1][1]

n=1/a
TxPower=b*n

un=np.sqrt(((-1/(a**2))**2)*(ua**2))
uTxPower=np.sqrt((n**2)*(ub)**2)

#Calculated distance from RSSI
d=10**((TxPower-rssi)/(10*n))
plt.figure(0)
plt.plot(d,rssi,marker='o',linestyle='', label='Teoria')
plt.legend()
plot.savefig('Results/kalibracja.png', format='png', dpi=600)

#Linear function
plot=plt.figure(1)
plt.plot(rssi[:-1],y,marker='o',linestyle='')
plt.plot(rssi[:-1],[-1*a*rssi1+b for rssi1 in rssi[:-1]],linestyle='-')
plt.xlabel('RSSI [dBm]'), plt.ylabel('$10\log_{10}(d)$ [j.u]')
plot.savefig('Results/kalibracja_dopasowanie.png', format='png', dpi=600)

print('a='+str(a)+' u(a)='+str(ua))
print('b='+str(b)+' u(b)='+str(ub))
print('n='+str(n)+' u(n)='+str(un))
print('TxPower='+str(TxPower)+' u(TxPower)='+str(uTxPower))
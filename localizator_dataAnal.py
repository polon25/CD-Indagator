# -*- coding: utf-8 -*-
"""
Created on Sun May  2 20:00:51 2021

@author: Polonius

Bunch of functions for data manipulation
"""

import path
import sqlite3
import datetime
import numpy as np
from os import path

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

def importBeacons(con):
    cursor=con.execute("SELECT * FROM beacons")
    return cursor.fetchall()

def str2datetime(text):
    return datetime.datetime.strptime(text, '%a %b %d %H:%M:%S %Y')

def str2seconds(text):
    timeSt=datetime.datetime.strptime(text, '%a %b %d %H:%M:%S %Y')
    return int(timeSt.timestamp())

def rssi2distance(rssiStr,n,TxPower,k): #in cm
    rssi=int(rssiStr[0:-3])
    return k*(10**((TxPower-rssi)/(10*n)))

def getContacts(data,interval):
    j=0
    contactsSameMoment=[]
    contactsAll=[]
    timeOld=data[0][1]
    for row in data:
        if abs(row[1]-timeOld)<=interval:
            contactsSameMoment.append(row)
            continue
        
        timeOld=row[1]
        contactsAll.append(contactsSameMoment)
        contactsSameMoment=[row]
        j+=1
    
    return contactsAll

def clearDuplicates(contacts):
    beaconOld=''
    for ii,point in enumerate(contacts):        
        for i,row in enumerate(point):
            if row[2]==beaconOld:
                del point[i]
                continue
            beaconOld=row[2]
        
        contacts[ii]=sorted(point,key=lambda x:x[-1]) #Sort from closest to longest distance
        
    return contacts

def getNearestBeacons(beaconsList, contactPoints, n): #Find n nearest beacons    
    if len(contactPoints)>=n: #If not enough points
        N=n
    else:
        N=len(contactPoints)
    
    beaconsNear=[]
    for i in range(N):
        for beacon in beaconsList:
            if beacon[0]==contactPoints[i][2]:
                beaconsNear.append(beacon)
                break
            
    return beaconsNear

def pointsToTableXYZR(beaconsList,contactPoints):
    x=[]
    y=[]
    z=[]
    r=[]
    for beacon,contact in zip(beaconsList,contactPoints):
        x.append(beacon[1])
        y.append(beacon[2])
        z.append(beacon[3])
        r.append(contact[-1])
    return x,y,z,r

def XYZRtoPoints(x,y,z,r):
    points=[]
    for x1,y1,z1,r1 in zip(x,y,z,r):
        points.append([x1,y1,z1,r1])
    return points

def get2pointsDistance2D(pointA, pointB):
    return abs(np.sqrt((pointA[0]-pointB[0])**2+(pointA[1]-pointB[1])**2))

def get2pointsDistance3D(pointA, pointB):
    return abs(np.sqrt((pointA[0]-pointB[0])**2+(pointA[1]-pointB[1])**2+(pointA[2]-pointB[2])**2))
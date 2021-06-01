# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 19:21:18 2021

@author: Polonius

Server of the setup of localization of a smartphone based on measured RSSI of Bluetooth beacons.

Program gets via wi-fi data about found BT devices around the smartphone.
If data is about one of beacons and is not a duplicate of previous one,
then it is saved in SQL database.

SQL database contains tables:
-beacons -> beacons' names and localizations in XYZ
-users -> user ID and its MAC address
-user<ID> -> information about founded beacon - time, name and RSSI

If data is received from unknown MAC, a new user is created.
"""

import socket
import sqlite3
from os import path

def dataConversion(data):
    dataArray=data.split('=')
    date=dataArray[0]
    date=date[2:] #Remove problematic null char
    date=date[:-14]+date[-4:] #Remove problematic timezone
    dataArray[0]=date
    return dataArray
    
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

#Open database
con=openDataBase('locBT_rooms.db')

#Previous received data
dataArrOld=[]

#Start server
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "192.168.1.13"
port = 8369
print (host)
print (port)
serversocket.bind((host, port))

serversocket.listen(5)
print ('server started and listening')
while True:
    #Read data sent via WiFi
    (clientsocket, address) = serversocket.accept()
    data = clientsocket.recv(1024).decode()
    dataArr=dataConversion(data)
    
    #If the same data was already received - often happens
    if dataArr==dataArrOld:
        continue
    dataArrOld=dataArr
    
    #If not Beacon, then don't send to dataBase
    if(dataArr[2].find('Beacon')<0):
        continue
       
    #Remove new line symbols
    dataArr[2].replace('\r\n','')
    
    print(dataArr)
    r='Receive'
    clientsocket.send(r.encode())
    
    #Check if user exist, if not add him and create his localization table
    cursor=con.execute("SELECT * FROM users WHERE mac='"+dataArr[1]+"'")
    userIDmac=cursor.fetchall()
    if(len(userIDmac)==0):
        #Add user to users table
        data=(dataArr[1],12)
        cursor=con.cursor()
        cursor.execute("""INSERT INTO users(mac) VALUES (?)""",data[0:1])
        con.commit()
        #Check user id
        cursor=con.execute("SELECT id FROM users WHERE mac='"+dataArr[1]+"'")
        userID=cursor.fetchall()[0][0]
        #Create table for that user
        con.execute("""CREATE TABLE user"""+str(userID)+"""(time TEXT, beacon TEXT, rssi TEXT);""")
        con.commit()
        userIDmac=[]
        userIDmac.append([userID,dataArr[1]])
    
    #Save data to database
    dataBeacon=(dataArr[0],dataArr[2],dataArr[3])
    cursor.execute("""INSERT INTO user"""+str(userIDmac[0][0])+"""(time, beacon, rssi) VALUES (?,?,?)""",dataBeacon)
    con.commit()
    
print("stop")
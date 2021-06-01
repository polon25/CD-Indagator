# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:48:41 2021

@author: Polonius

Script for simplified localization of a smartphone based on measured RSSI of Bluetooth beacons.
Program reads data from SQL database containing tables:
-beacons -> beacons' names and localizations in XYZ
-users -> user ID and its MAC address
-user<ID> -> information about founded beacon - time, name and RSSI

For each timepoint distance of each Beacon is calculated based on RSSI values.
Smartphone localization is based on the closest beacon.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import confusion_matrix
from localizator_dataAnal import *   

#Experimental params - gained after calibrations
n=4.293667341048177
TxPower=10.279889735494974
k=1 #Pilka's constant

#Testing parameters - when and where the smarphone actually was
roomChangeTime=['Sun May 23 15:25:00 2021','Sun May 23 15:30:00 2021',
                'Sun May 23 15:35:00 2021','Sun May 23 15:40:00 2021']
targetBeacons=['Beacon001','Beacon002','Beacon003','Beacon004']
roomsNames=['Kuchnia','Salon','Sypialnia','Łazienka']

roomChangeSec=[str2seconds(time) for time in roomChangeTime]
roomChangeSec.append(roomChangeSec[-1]+9999999)
del roomChangeTime

#Importing data from the database    
con=openDataBase('locBT_rooms.db')
dataOrg=importUser(con,'1')
beaconsList=importBeacons(con)

#datetime, seconds from 0, beaconID, distance [cm]
data=[tuple([str2datetime(row[0]),str2seconds(row[0]),row[1],rssi2distance(row[2],n,TxPower,k)]) for row in dataOrg]

contactPoints=getContacts(data,10)
contactPoints=clearDuplicates(contactPoints)

#Get only the closest ones
closestBeacons=[contactPoint[0][1:3] for contactPoint in contactPoints]
del dataOrg, contactPoints, data, k, n, TxPower

#Create list with target beacons for each moment
targetBeaconsList=[]
predictedBeaconsList=[]
timeInter=0#In which period we are
for moment in closestBeacons:
    if moment[0]>roomChangeSec[timeInter+1]:
        timeInter+=1
        
    targetBeaconsList.append(targetBeacons[timeInter])
    predictedBeaconsList.append(moment[1])
    
del moment, timeInter

#Confusion Matrix
confMatrix=confusion_matrix(targetBeaconsList,predictedBeaconsList)

#Drawing confusion matrix
confMatrixDF=pd.DataFrame(confMatrix,index=roomsNames,columns=roomsNames)
confMatrixPlot = plt.figure()
sns.heatmap(confMatrixDF, annot=True, cbar=None, cmap='Oranges')
plt.title('Macierz pomyłek')
plt.ylabel('Pokój rzeczywisty'),plt.xlabel('Pokój znaleziony')
plt.show()
confMatrixPlot.savefig('Results/rooms_confMatrix.png', format='png', dpi=600)


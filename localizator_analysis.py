# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 15:48:41 2021

@author: Polonius

Script for localization of a smartphone based on measured RSSI of Bluetooth beacons.
Program reads data from SQL database containing tables:
-beacons -> beacons' names and localizations in XYZ
-users -> user ID and its MAC address
-user<ID> -> information about founded beacon - time, name and RSSI

For each timepoint distance of each Beacon is calculated based on RSSI values.
We can treat the distance as a radius of sphere with the beacon in the center,
so localization of the smarphone is where such spheres intersect.

Used fragments of code written by someone else:
Functions for finding intersections of two circles is written by scleronomic:
https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
Functions for solving three sphere intersection problem is written by vvhitedog:
https://github.com/vvhitedog/three_sphere_intersection
"""

import numpy as np                                    

import operator
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from localizator_dataAnal import *
from intersec2D import *
from intersec3D import *     
    
def findPoint2D(beaconsList, contactPoints):
    #Find 3 nearest beacons
    beaconsNear=getNearestBeacons(beaconsList, contactPoints, 3)
            
    #Get parameters of "field circles" around beacons
    x,y,z,r=pointsToTableXYZR(beaconsNear,contactPoints)
    points=XYZRtoPoints(x,y,z,r)
    
    #Get the closer beacon to the closest one
    #and for them calculate intersections of "field circles"
    #then use third one to determine which of two potential points is closer
    
    if get2pointsDistance2D(points[0],points[1])<get2pointsDistance3D(points[0],points[2]):
        intersections = get_intersections(x[0], y[0], r[0], x[1], y[1], r[1])
        ix0, iy0, ix1, iy1 = intersections   
        d1=abs(np.sqrt((x[2]-ix0)**2+(y[2]-iy0)**2)-r[2])
        d2=abs(np.sqrt((x[2]-ix1)**2+(y[2]-iy1)**2)-r[2])        
    else:
        intersections = get_intersections(x[0], y[0], r[0], x[2], y[2], r[2])
        ix0, iy0, ix1, iy1 = intersections   
        d1=abs(np.sqrt((x[1]-ix0)**2+(y[1]-iy0)**2)-r[1])
        d2=abs(np.sqrt((x[1]-ix1)**2+(y[1]-iy1)**2)-r[1])
    
    if d1<d2:
        return ix0,iy0
    else:
        return ix1,iy1
    
def findPoint3D(beaconsList, contactPoints):
    #Find 3 nearest beacons
    beaconsNear=getNearestBeacons(beaconsList, contactPoints, 4)
            
    #Get parameters of "field circles" around beacons
    x,y,z,r=pointsToTableXYZR(beaconsNear,contactPoints)
    
    if len(x)==3:
        x.append(x[-1])
        y.append(y[-1])
        z.append(z[-1])
        r.append(r[-1])
    elif len(x)<3:
        return [0,0,0]
        
    points=XYZRtoPoints(x,y,z,r)
    
    fieldSpheres=[Sphere(np.array([x1,y1,z1]),r1) for x1,y1,z1,r1 in zip(x,y,z,r)]
    
    #Get the closest pair - to point 0 and to object    
    beaconDist=[]   
    for i in range(len(x)-1):
        beaconDist.append([get2pointsDistance3D(points[0],points[i+1]),r[i+1],i+1])
    beaconDist = sorted(beaconDist, key=operator.itemgetter(0, 1)) #Sort by 2 values
    
    circle=fieldSpheres[0].get_circle_of_intersection(fieldSpheres[beaconDist[0][-1]])
    ret_value = fieldSpheres[beaconDist[1][-1]].find_intersection_with_circle(circle)
               
    if ret_value is None:
        return [0,0,0]
    
    if get2pointsDistance3D(ret_value[0],points[beaconDist[2][-1]])<get2pointsDistance3D(ret_value[1],points[beaconDist[2][-1]]):
        return ret_value[0]
    else:
        return ret_value[1]

#Experimental params - gained after calibrations
n=4.293667341048177
TxPower=10.279889735494974
k=4 #Polonius' constant
outputPlotName='test'
    
#Open databese and import data of single, specified user
con=openDataBase('locBT_outside_circle.db')
dataOrg=importUser(con,'1')
beaconsList=importBeacons(con)

#Prepering data for analysis

#datetime, seconds from 0, beaconID, distance [cm]
data=[tuple([str2datetime(row[0]),str2seconds(row[0]),row[1],rssi2distance(row[2],n,TxPower,k)]) for row in dataOrg]

contactPoints=getContacts(data,10)
contactPoints=clearDuplicates(contactPoints)

beaconPointsX=[beacon[1] for beacon in beaconsList]
beaconPointsY=[beacon[2] for beacon in beaconsList]
beaconPointsZ=[beacon[3] for beacon in beaconsList]

contactPoint=contactPoints[0]

#Find intersections - where was the smartphone?
#points=[[x for x in findPoint2D(beaconsList, contactPoint)] for contactPoint in contactPoints]
pointsA=[[x for x in findPoint3D(beaconsList, contactPoint)] for contactPoint in contactPoints]
x2D=[point[0] for point in pointsA]
y2D=[point[1] for point in pointsA]

#Plot results - where were beacons and smartphone?
plot=plt.figure(0)
plt.plot(beaconPointsX,beaconPointsY,marker='o',linestyle='')
plt.plot(x2D,y2D,marker='o',linestyle='')
plt.ylabel('y [cm]'),plt.xlabel('x [cm]')
plot.savefig('Results/'+outputPlotName+'.png', format='png', dpi=600)
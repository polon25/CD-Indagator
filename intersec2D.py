# -*- coding: utf-8 -*-
"""
Created on Sun May  2 20:06:44 2021

Function written by scleronomic
https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
"""

import math

def get_intersections(x0, y0, r0, x1, y1, r1): #From StackOverflow
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)

    # non intersecting
    if d > r0 + r1 :
        return {}
    # One circle within other
    if d < abs(r0-r1):
        return {}
    # coincident circles
    if d == 0 and r0 == r1:
        return {}
    else:
        a=(r0**2-r1**2+d**2)/(2*d)
        h=math.sqrt(r0**2-a**2)
        x2=x0+a*(x1-x0)/d   
        y2=y0+a*(y1-y0)/d   
        x3=x2+h*(y1-y0)/d     
        y3=y2-h*(x1-x0)/d 
        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d
        return x3, y3, x4, y4  
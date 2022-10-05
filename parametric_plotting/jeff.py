#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import numpy library
import numpy as np
import math
import logging

# Parametric equations in cartesian co-ordinates
# Parametres
a = 1
a2 = 3
b = -1
b2 = -10

# y=ax+b is transformed to a1x+b1y+c1=0
def affine_to_params(a,b):
    a1 = -a
    b1 = 1
    c1 = -b
    return a1,b1,c1

# a1x+b1y+c1=0 is transformed to y=ax+b
def params_to_affine(a1, b1, c1):
    a = -a1/b1
    b = -c1/b1
    return a,b

def get_angle(affine1, affine2):
    q = (affine2[0]-affine1[0])/(1+affine2[0]*affine1[0])
    return math.atan(np.abs(q))

def rad2deg(angle):
    return angle*180/np.pi

def deg2rad(angle):
    return angle*np.pi/180

def intersection(affine1, affine2):
    x = (affine2[1]-affine1[1])/(affine1[0]-affine2[0])
    y = affine1[0]*x+affine1[1]
    return x,y

def split_angle(line1, line2):
    result = []
    affine1 = line1
    affine2 = line2
    if(affine2[0]<affine1[0]):
        affine1 = line2
        affine2 = line1
    #amount_intervals = 1
    amount_intervals = 19
    radians = get_angle(affine1, affine2)
    logging.log(50,"split_angle between %s " % rad2deg(math.atan(affine1[0])))
    logging.log(50,"split_angle AND %s " % rad2deg(math.atan(affine2[0])))
    for i in range(0,amount_intervals):
        index_incr = i+0.5
        logging.log(50,"split_angle %s " % (index_incr))
        angle = radians*(index_incr/amount_intervals)
        logging.log(50,"split_angle %s " % rad2deg(angle))
        logging.log(50,"angle= %s " % (rad2deg(angle)+rad2deg(math.atan(affine1[0]))))
        affineA = math.tan(angle+math.atan(affine1[0]))
        logging.log(50,"a1= %s " % (affineA))
        x,y = intersection(affine1, affine2)
        logging.log(50,"intersection= {0} ".format( (x,y)))
        affineB = y-affineA*x
        result.append((affineA,affineB),)
    return result

# Import plotting libraries
import matplotlib.pyplot as plt
# Create some mock data
#t = np.arange(0.01, 10.0, 0.01)
t = np.linspace(-30, 30, 1000)
data1 = a*t+b
#data1 = np.exp(t)
data2 = a2*t+b2
#data2 = np.sin(2 * np.pi * t)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(t, data1, 'r') # plotting t, a separately
ax.plot(t, data2, 'b') # plotting t, b separately

affine1 = (a,b)
affine2 = (a2,b2)
angle_between = get_angle(affine1, affine2)
bissecs = split_angle(affine1, affine2)
for bissec in bissecs:
    data3 = bissec[0]*t+bissec[1]
    ax.plot(t, data3, 'g') # plotting t, b separately

ax.set_title('line plot with data points {0}'.format(rad2deg(angle_between)))
#ax.set_title('line plot with data points {0}'.format(intersection((a,b), (a2,b2))))
plt.show()
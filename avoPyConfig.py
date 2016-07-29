#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 10-7-2016

# File Name: avoPyConfig.py

# Synopsis:
# Contains all the starting configuration data for avoPy

# Calling:
# 

###############################################################################
'''
from data.structLith import structLith, structAVOMod

nsim=200
nvar=0.4
std=1.5    

lith1=structLith('88Shale','purple',3418.495962,1752.987063,2.511256121,
                          135.4004251,87.36126824,0.02921484
                          )
lith2=structLith('86Shale','purple',3136.638766,1551.366701,2.451602365,
                          136.9440216,69.52937955,0.051839809
                          )
lith3=structLith('FlaxSand','orange',3663.504934,2034.815946,2.350170833,
                          660.7719596,237.4747584,0.11979099
                          )
lith4=structLith('WarC_NorPor_Brine','darkblue',3792.742707,2232.982847,2.321682669,
                          121.1846522,114.0411247,0.01972362
                          )
lith5=structLith('WarC_NorPor_Gas','darkred',3660.358995,2300.630797,2.186832257,
                          135.8816038,116.0905371,0.024889946
                          )
lith6=structLith('WarC_LowPor_Brine','blue',3705.559909,2069.811364,2.373842343,
                          329.6156111,242.0803495,0.076480652
                          )
lith7=structLith('WarC_LowPor_Gas','red',3634.742642,2106.368042,2.300648574,
                          329.023622,268.5826829,0.131645288
                          )
lith8=structLith('Coal','green',2961.5,1563.465,2.045182162,
                          212.9567022,117.2511315,0.082144079
                          )

#lithAr=[lith1,lith2,lith3,lith4,lith5,lith6,lith7,lith8]

lithAr = [lith1,lith2,lith4,lith5,lith6,lith7,lith8]
intfAr=[[lith1,lith1,'purple'],
        [lith1,lith4,'darkblue'],
        [lith1,lith5,'darkred'],
        [lith1,lith6,'blue'],
        [lith1,lith7,'red'],
        [lith1,lith8,'green']]


#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 10-7-2016

# File Name: avoPy.py

# Synopsis:
# Create a plot with blocky avo outputs.

# Calling:
# 

###############################################################################
'''
from func.funcAVOModels import *
from data.structLith import structLith, structAVOMod

nsim=200
nvar=0.4    

lith1=structLith('88Shale','purple',3418.495962,1752.987063,2.511256121,
                          135.4004251,87.36126824,0.02921484
                          )
lith2=structLith('86Shale','lightpurple',3136.638766,1551.366701,2.451602365,
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

for lith in lithAr:
    lith.calcModel(nsim,nvar)

intfMod=[]    
for intf in intfAr:
    intfMod.append(structAVOMod(intf[0],intf[1],nsim,nvar,intf[2]))


#from bokeh.layouts import gridplot
from bokeh.io import gridplot
from bokeh.plotting import figure, output_file, show, output_notebook
from bokeh.resources import INLINE


output_file('avo_test.html',mode='inline')
#output_notebook(resources=INLINE)

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave,box_select,poly_select,lasso_select"

#AVO FIGURE
pAVO = figure(
    tools=TOOLS,
    title="AVO Intercept vs Gradient",
    y_range=[-0.5,0.5],x_range=[-0.5,0.5],
    x_axis_label='Intercept',y_axis_label="Gradient")

pAVO.grid.grid_line_width = 2

for intf in intfMod:
    pAVO.circle(intf.AVOMod[:,6],
                intf.AVOMod[:,7],
                color=intf.colour,
                fill_color="none",
                legend=intf.name,                
                size=5)

#RPRS FIGURE
pRPRS = figure(
    tools=TOOLS,
    title="Rp vs Rs",
    y_range=[-0.5,0.5],x_range=[-0.5,0.5],
    x_axis_label="Rp",y_axis_label="Rs")

for intf in intfMod:
    pRPRS.circle(intf.AVOMod[:,6],
                 intf.AVOMod[:,8],
                 color=intf.colour,
                 fill_color="none",
                 legend=intf.name,                
                 size=5)

#pRPRS.legend.location="bottom_right"
pRPRS.grid.grid_line_width = 2

#AI vs VPVS
pAIVPVS = figure(
    tools=TOOLS,
    title="AI vs VpVs",
    x_axis_label="Acoustic Impedance",y_axis_label="VpVs")

for lith in lithAr:
    pAIVPVS.circle(lith.AIMod,lith.VPVSMod,color=lith.colour,fill_color="none",
                 legend=lith.name,                
                 size=3)

pAIVPVS.grid.grid_line_width = 2

p = gridplot([[pAVO,pRPRS],[None,pAIVPVS]])


#show(p)    
#x=calcRandNorm(3660,135,0.77,0.05)
#print(x)
#y=calcRandNorm(3660,135,np.random.rand(10),0.05)
#print(y)

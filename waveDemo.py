#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 30-7-2016

# File Name: waveDemo.py

# Synopsis:
# Create a plot with editable wavelets.

# Calling:
# 

###############################################################################
'''
from func.funcWave import *
from func.funcFilter import *
from data.structWave import structWave
from templates.plots import *

import bokeh.layouts as bkl
import bokeh.plotting as bkp
import bokeh.models as bkm
import bokeh.models.widgets as bkw

bkp.output_file('waveletDemo.html',mode='inline')

wave1=structWave('Ricker25','red',512,0.5)
wave1.typeRicker(25)
wave1.calcAmpSpec()

wave2=structWave('BP 5,10,50,70','green',512,0.5)
wave2.typeBandPass(5,10,50,70)
wave2.calcAmpSpec()

wave3=structWave('Ormsby 5,10,50,70','blue',512,0.5)
wave3.typeOrmsby(5,10,50,70)
wave3.calcAmpSpec()

pwave1=bkp.Figure(title='Time Amplitude',x_axis_label='Time',webgl=True)
pwave2=bkp.Figure(title='Amplitude Spectrum',x_axis_label='Freq',webgl=True)

sw1 = bkm.ColumnDataSource(data=dict(time=wave1.timeseries,B=wave1.timeAmp))
sw2 = bkm.ColumnDataSource(data=dict(time=wave2.timeseries,B=wave2.timeAmp))
sw3 = bkm.ColumnDataSource(data=dict(time=wave3.timeseries,B=wave3.timeAmp))
sf1 = bkm.ColumnDataSource(data=dict(freq=wave1.freqseries,B=wave1.ampSpec))
sf2 = bkm.ColumnDataSource(data=dict(freq=wave2.freqseries,B=wave2.ampSpec))
sf3 = bkm.ColumnDataSource(data=dict(freq=wave3.freqseries,B=wave3.ampSpec))

#pwave1.line('time','B',color=wave1.colour,source=sw1)
pwave1.line('time','B',color=wave2.colour,source=sw2)
#pwave1.line('time','B',color=wave3.colour,source=sw3)
pwave2.line('freq','B',color=wave1.colour,source=sf1)
pwave2.line('freq','B',color=wave2.colour,source=sf2)
pwave2.line('freq','B',color=wave3.colour,source=sf3)

waveletslayout=bkl.row(pwave1,pwave2)

x,y=makeLowPass(100,1.,10,15)
u,v=makeHighPass(100,1.,40,55)
s,t=makeBandPass(100,1.,10,15,40,55)

lpplot=bkp.Figure(title='Low Pass',x_axis_label='Freq (Hz)',webgl=True)
hpplot=bkp.Figure(title='High Pass',x_axis_label='Freq (Hz)',webgl=True)
bpplot=bkp.Figure(title='Band Pass',x_axis_label='Freq (Hz)',webgl=True)

slp=bkm.ColumnDataSource(data=dict(freq=x,Amp=y))
shp=bkm.ColumnDataSource(data=dict(freq=u,Amp=v))
sbp=bkm.ColumnDataSource(data=dict(freq=s,Amp=t))

lpplot.line('freq','Amp',source=slp)
hpplot.line('freq','Amp',source=shp)
bpplot.line('freq','Amp',source=sbp)

filterplots=bkl.row(lpplot,hpplot,bpplot)

tab1 = bkw.Panel(child=waveletslayout,title='Wavelets')
tab2 = bkw.Panel(child=filterplots,title='Filters')
tabs = bkw.Tabs(tabs = [tab1,tab2])
bkp.show(tabs)
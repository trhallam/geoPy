#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 30-7-2016

# File Name: rickerDemo.py

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

import bokeh.io as bki
import bokeh.layouts as bkl
import bokeh.plotting as bkp
import bokeh.models as bkm
import bokeh.models.widgets as bkw

#bkp.output_file('ricker32Demo.html',mode='inline')
bkp.output_server('RickerDemo')

wave1=structWave('Ricker25','red',512,0.5)
wave1.typeRicker(25)
wave1.calcAmpSpec()

pwave1=bkp.figure(title='Time Amplitude',x_axis_label='Time',webgl=True)
pwave2=bkp.figure(title='Amplitude Spectrum',x_axis_label='Freq',webgl=True)

sw1 = bkm.ColumnDataSource(data=dict(time=wave1.timeseries,B=wave1.timeAmp))
sf1 = bkm.ColumnDataSource(data=dict(freq=wave1.freqseries,B=wave1.ampSpec))

pwave1.line('time','B',color=wave1.colour,source=sw1)
pwave2.line('freq','B',color=wave1.colour,source=sf1)

waveletslayout=bkl.column(pwave1,pwave2)

#set up widgets
domFreq = bkw.Slider(title="Dom Frequency", value=25, start=0, end=50.0, step=1)




# Set up callbacks
def update_data(attrname, old, new):

    # Get the current slider values
    dF = domFreq.value

    # Generate the new curve
    wave1.typeRicker(dF)
    wave1.calcAmpSpec()
    print('update')
    sw1.data=dict(time=wave1.timeseries,B=wave1.timeAmp)
    sf1.data=dict(freq=wave1.freqseries,B=wave1.ampSpec)

domFreq.on_change('value', update_data)
inputs = bkl.widgetbox(domFreq)

bki.curdoc().add_root(bkl.row(inputs,waveletslayout,width=300))
bki.curdoc().title='Ricker'
#bkp.show(bkl.row(inputs,waveletslayout))

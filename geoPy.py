#!/usr/bin/python

###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 11-9-2018

# File Name: geoPy.py

# Synopsis:
# Main program for geoPy 1D reflection interface modelling.
# Runs as bokeh module.

# Calling:
# bokeh serve --show geoPy.py

###############################################################################

from os.path import dirname, join

import pandas as pd
import numpy as np

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.widgets import DataTable, TableColumn, Select, Tabs, Panel, Slider, Div

from data.structLith import structMineral, structFluid, structDryFrame, structRock
from layouts import fdi, dims

# Initial Data
inputs = 'inputs'
fr = join(dirname(__file__), inputs, 'geoPy_rocks.csv')
ff = join(dirname(__file__), inputs, 'geoPy_fluids.csv')
fp = join(dirname(__file__), inputs, 'geoPy_pres.csv')
idepth = 3180 #mTVDSS

pagewidth = 1000 #pixels
presmin=5; presmax = 35;

# Plotting
# AVO Reflectivity
avosource = dict()
avofig = figure(title="Amplitude of Reflectivity vs Offset(deg)", tools="wheel_zoom,pan,reset")

# AVO Stochastic Modelling
avostatsource = dict()
avostatfig = figure(title="Intercept vs Gradient", tools="wheel_zoom,pan,reset")

# 4D Impedance
plot_scale = 100 + 1
fourdimp = fdi.widgetFDI(plot_scale, 5, 25)

# Input Panels
gp_dims = dims.widgetDIMS(idepth,fr,ff,fp,fdi=fourdimp)

#Layout of Page
plottab1 = Panel(child=avofig, title='AVO Reflectivity')
plottab2 = Panel(child=avostatfig, title='Stochastic AVO')
plottab3 = Panel(child=fourdimp.layout, title='4D Impedance')

plottabs = Tabs(tabs=[plottab1,plottab2,plottab3],width=pagewidth)

#update()
curdoc()
curdoc().add_root(column(gp_dims.layout,plottabs,width=pagewidth))
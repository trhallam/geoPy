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
from layouts import fdi

# Initial Data
datarocks = pd.read_csv(join(dirname(__file__), 'inputs\geoPy_rocks.csv'),skipinitialspace=True)
datafluids = pd.read_csv(join(dirname(__file__),'inputs\geoPy_fluids.csv'),skipinitialspace=True)
datapres = pd.read_csv(join(dirname(__file__),'inputs\geoPy_pres.csv'),skipinitialspace=True)
idepth = 3180 #mTVDSS
pagewidth = 1000 #pixels
presmin=5; presmax = 35;

# Setup Sources
sourcerocks = ColumnDataSource(datarocks)
sourcefluids = ColumnDataSource(datafluids)
sourcepres = ColumnDataSource(datapres)


namesrocks = datarocks.Name.tolist()
namesfluids = datafluids.Name.tolist()
namespres = datapres.Name.tolist()

columnrocks = [TableColumn(field=Ci, title=Ci) for Ci in datarocks.columns]
columnfluids = [TableColumn(field=Ci, title=Ci) for Ci in datafluids.columns]
columnpres = [TableColumn(field=Ci, title=Ci) for Ci in datapres.columns]
columnoutput = [TableColumn(field='rock', title='rock'),
                TableColumn(field='fluid', title='fluid'),
                TableColumn(field='Vp', title='Vp'),
                TableColumn(field='Vs', title='Vs'),
                TableColumn(field='rho', title='rho'),
                TableColumn(field='other', title='other')]

# Define outputs
sourceoutput = ColumnDataSource(data=dict())

# Define Updates

def update():
    columnoutput = []
    selv, seli = get_selections()
    #    0    1     2     3     4     5        0     1      2      3      4
    #[obrv,obfv,resrv,resfv,presv,depth], [obrvi,obfvi,resrvi,resfvi,presvi]
    #   0     1      2       3        4         5          6     7    8      9     10     11     12
    #Name,kclay,muclay,rhoclay,knonclay,munonclay,rhononclay,vclay, phi, dryEk, dryPk, dryEg, dryPg
    obrock = datarocks.loc[seli[0]]; obfluid = datafluids.loc[seli[1]]
    resrock = datarocks.loc[seli[2]]; resfluid = datafluids.loc[seli[3]]
    #   0   1     2   3     4   5     6   7   8   9
    #Name, ko, rhoo, kw, rhow, kg, rhog, so, sw, sg
    pres = datapres.loc[seli[4]]
    depth = selv[5]

    #set model rock mineral assemblages
    parnonclay = ['knonclay', 'munonclay', 'rhononclay']; parclay = ['kclay', 'muclay', 'rhoclay']
    obnonshale = structMineral('nonshale',*[obrock[par] for par in parnonclay])
    obshale = structMineral('shale',*[obrock[par] for par in parclay])
    nonshale = structMineral('nonshale',*[resrock[par] for par in parnonclay])
    shale = structMineral('shale',*[resrock[par] for par in parclay])
    #output rock names to table
    sourceoutput.data['rock'] = [obrock['Name'],resrock['Name']]

    # oil, water, gas, setup and mixing
    #park = ['ko', 'kw', 'kg']; parrho = ['rhoo', 'rhow', 'rhog']; pars = ['so', 'sw', 'sg']
    parw = ['kw', 'rhow', 'sw']; paro = ['ko', 'rhoo', 'so']; parg = ['kg', 'rhog', 'sg']
    obfluidmix = structFluid(obfluid['Name'], water=[obfluid[ind] for ind in parw],
                                              oil=[obfluid[ind] for ind in paro],
                                              gas=[obfluid[ind] for ind in parg])
    resfluidmix = structFluid(resfluid['Name'], water=[obfluid[ind] for ind in parw],
                                                oil=[obfluid[ind] for ind in paro],
                                                gas=[obfluid[ind] for ind in parg])
    #output fluid names to table
    sourceoutput.data['fluid'] = [obfluid['Name'],resfluid['Name']]

    #Calculate dry rock frames for OB and Res
    obdryrock = structDryFrame(obrock['Name'], obnonshale, obshale, obrock['vclay'], obrock['phi'])
    resdryrock = structDryFrame(resrock['Name'], nonshale, shale, resrock['vclay'], resrock['phi'])
    obdryrock.calcRockMatrix(); resdryrock.calcRockMatrix()
    parp = ['init_Pres', 'curr_Pres']; pardry = ['dryEk', 'dryPk', 'dryEg', 'dryEk']
    obdryrock.calcDryFrame(pres['OB_Grad'], depth, *[pres[par] for par in parp], *[obrock[par] for par in pardry])
    resdryrock.calcDryFrame(pres['OB_Grad'], depth, *[pres[par] for par in parp], *[resrock[par] for par in pardry])

    #calculate rock models and properties
    obrockmodel = structRock(obdryrock, obfluidmix)
    obrockmodel.calcGassmann(); obrockmodel.calcDensity(); obrockmodel.calcElastic()
    resrockmodel = structRock(resdryrock, resfluidmix)
    resrockmodel.calcGassmann(); resrockmodel.calcDensity(); resrockmodel.calcElastic()

    #output rockproperties to table
    sourceoutput.data['Vp'] = [obrockmodel.velp,resrockmodel.velp]
    sourceoutput.data['Vs'] = [obrockmodel.vels,resrockmodel.vels]
    sourceoutput.data['rho'] = [obrockmodel.den, resrockmodel.den]
    sourceoutput.data['other'] = [obrockmodel.pimp, resrockmodel.pimp]

    #test impedance 4d
    #fourdimp.calcDImp(fourdimpsource, fourdvecsource, plot_scale, resdryrock, resfluidmix, presmin, presmax, resrockmodel.pimp)
    fourdimp.updateModel(resdryrock,resfluidmix,5,25,init_imp=resrockmodel.pimp)

#Setup DataTables
tablekwargs = dict(); tablekwargs['width'] = pagewidth; tablekwargs['editable']=True
tablerocks = DataTable(source=sourcerocks, columns=columnrocks, **tablekwargs)
tablefluids = DataTable(source=sourcefluids, columns=columnfluids, **tablekwargs)
tablepres = DataTable(source=sourcepres, columns=columnpres, **tablekwargs)
tableoutput = DataTable(source=sourceoutput, columns=columnoutput, **tablekwargs)

#Setup Select Panes
selectobr = Select(value=namesrocks[0],options=namesrocks, title="Rock  Model")
selectresr = Select(value=namesrocks[0],options=namesrocks, title="Rock  Model")
selectobf = Select(value=namesfluids[0],options=namesfluids, title="Fluid Model")
selectresf = Select(value=namesfluids[0],options=namesfluids, title="Fluid Model")
selectpres = Select(value=namespres[0],options=namespres, title="Pressure Scenario")
slidedepth = Slider(start=0,end=10000,value=idepth,step=1,title='Depth (m)')

def get_index(value,names):
    return names.index(value)

def get_selections():
    obrv, obfv = selectobr.value, selectobf.value
    resrv, resfv = selectresr.value, selectresf.value
    presv = selectpres.value
    depth = slidedepth.value
    obrvi = get_index(obrv,namesrocks); obfvi=get_index(obfv,namesfluids)
    resrvi = get_index(resrv,namesrocks); resfvi=get_index(resfv,namesfluids)
    presvi = get_index(presv,namespres)
    return [obrv,obfv,resrv,resfv,presv,depth], [obrvi,obfvi,resrvi,resfvi,presvi]

#Setup Updates
def selection_change(attrname, old, new):
    update()

selectobr.on_change('value',selection_change)
selectresr.on_change('value',selection_change)
selectobf.on_change('value',selection_change)
selectresf.on_change('value',selection_change)
selectpres.on_change('value',selection_change)
slidedepth.on_change('value',selection_change)

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

#Layout of Page
inputtab1 = Panel(child=tablerocks, title='Rock Models')
inputtab2 = Panel(child=tablefluids, title='Fluid Mixes')
inputtab3 = Panel(child=tablepres, title='Pressure Scenarios')
inputtab4 = Panel(child=tableoutput, title='Model Calculations')

inputtabs = Tabs(tabs=[inputtab1,inputtab2,inputtab3,inputtab4],width=pagewidth,height=200)

textrowob = Div(text="<h1> Overburden: </h1>")
selectrowob = row(selectobr,selectobf,width=500,height=50,sizing_mode="scale_both")
textrowres = Div(text="<h1> Reservoir: </h1>")
selectrowres = row(selectresr,selectresf,width=500,height=50,sizing_mode="scale_both")
selectrowpres = row(selectpres,slidedepth,width=500,height=50,sizing_mode="scale_both")

plottab1 = Panel(child=avofig, title='AVO Reflectivity')
plottab2 = Panel(child=avostatfig, title='Stochastic AVO')
plottab3 = Panel(child=fourdimp.layout, title='4D Impedance')

plottabs = Tabs(tabs=[plottab1,plottab2,plottab3],width=pagewidth)


update()
curdoc()
curdoc().add_root(column(inputtabs,
                         textrowob,selectrowob,textrowres,selectrowres,selectrowpres,
                         plottabs,width=pagewidth))
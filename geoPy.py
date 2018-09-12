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

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.widgets import DataTable, TableColumn, Select, Tabs, Panel, Slider, PreText

from data import structLith

# Initial Data
datarocks = pd.read_csv(join(dirname(__file__), 'geoPy_rocks.csv'),skipinitialspace=True)
datafluids = pd.read_csv(join(dirname(__file__),'geoPy_fluids.csv'),skipinitialspace=True)
datapres = pd.read_csv(join(dirname(__file__),'geoPy_pres.csv'),skipinitialspace=True)
idepth = 3180 #mTVDSS
pagewidth = 1000 #pixels

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
    pres = datapres.loc[seli[3]]
    depth = selv[5]


    #set rock mineral assemblages
    obnonshale = structLith.structMineral('nonshale',obrock['knonclay'],obrock['munonclay'],obrock['rhononclay'])
    obshale = structLith.structMineral('shale',obrock['kclay'],obrock['muclay'],obrock['rhoclay'])
    nonshale = structLith.structMineral('nonshale', resrock['knonclay'],resrock['munonclay'],resrock['rhononclay'])
    shale = structLith.structMineral('shale', resrock['kclay'], resrock['muclay'], resrock['rhoclay'])
    #output rock names to table
    sourceoutput.data['rock'] = [obrock['Name'],resrock['Name']]
    #columnoutput.append(TableColumn(field='rock', title='rock'))

    # oil, water, gas
    obfluidmix = structLith.structFluid(obfluid['Name'], [obfluid['ko'],obfluid['kw'],obfluid['kg']],
                                                      [obfluid['rhoo'], obfluid['rhow'], obfluid['rhog']],
                                                      [obfluid['so'], obfluid['sw'], obfluid['sg']])
    obfluidmix.mixfluids()
    resfluidmix = structLith.structFluid(resfluid['Name'], [resfluid['ko'],resfluid['kw'],resfluid['kg']],
                                                      [resfluid['rhoo'], resfluid['rhow'], resfluid['rhog']],
                                                      [resfluid['so'], resfluid['sw'], resfluid['sg']])
    resfluidmix.mixfluids()
    #output fluid names to table
    sourceoutput.data['fluid'] = [obfluid['Name'],resfluid['Name']]

    #Calculate dry rock frames for OB and Res
    obdryrock = structLith.structDryFrame(obrock['Name'], obnonshale, obshale, obrock['vclay'], obrock['phi'])
    resdryrock = structLith.structDryFrame(resrock['Name'], nonshale, shale, resrock['vclay'], resrock['phi'])
    print('create dry rock')
    obdryrock.calcRockMatrix(); resdryrock.calcRockMatrix()
    print('rock matrix')
    obdryrock.calcDryFrame(pres['OB_Grad'], depth, pres['init_Pres'], pres['curr_Pres'],
                           obrock['dryEk'],obrock['dryPk'],obrock['dryEg'],obrock['dryEk'])
    resdryrock.calcDryFrame(pres['OB_Grad'], depth, pres['init_Pres'], pres['curr_Pres'],
                           resrock['dryEk'],resrock['dryPk'],resrock['dryEg'],resrock['dryEk'])

    #calculate rock models and properties
    obrockmodel = structLith.structRock(obdryrock, obfluidmix)
    obrockmodel.calcGassmann(); obrockmodel.calcDensity(); obrockmodel.calcElastic()
    resrockmodel = structLith.structRock(resdryrock, resfluidmix)
    resrockmodel.calcGassmann(); resrockmodel.calcDensity(); resrockmodel.calcElastic()

    #output rockproperties to table
    sourceoutput.data['Vp'] = [obrockmodel.velp,resrockmodel.velp]
    sourceoutput.data['Vs'] = [obrockmodel.vels,resrockmodel.vels]
    sourceoutput.data['rho'] = [obrockmodel.den, resrockmodel.den]
    sourceoutput.data['other'] = [obrockmodel.pimp, resrockmodel.pimp]

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
fourdimpfig = figure(title="Delta Impedance for Pres vs Saturation", tools="wheel_zoom,pan,reset")

#Layout of Page
inputtab1 = Panel(child=tablerocks, title='Rock Models')
inputtab2 = Panel(child=tablefluids, title='Fluid Mixes')
inputtab3 = Panel(child=tablepres, title='Pressure Scenarios')
inputtab4 = Panel(child=tableoutput, title='Model Calculations')

inputtabs = Tabs(tabs=[inputtab1,inputtab2,inputtab3,inputtab4],width=pagewidth,height=200)

textrowob = PreText(text="Overburden",width=pagewidth,height=50)
selectrowob = row(selectobr,selectobf,width=500,height=50,sizing_mode="scale_both")
textrowres = PreText(text="Reservoir",width=pagewidth,height=50)
selectrowres = row(selectresr,selectresf,width=500,height=50,sizing_mode="scale_both")
selectrowpres = row(selectpres,slidedepth,width=500,height=50,sizing_mode="scale_both")

plottab1 = Panel(child=avofig, title='AVO Reflectivity')
plottab2 = Panel(child=avostatfig, title='Stochastic AVO')
plottab3 = Panel(child=fourdimpfig, title='4D Impedance')

plottabs = Tabs(tabs=[plottab1,plottab2,plottab3],width=pagewidth)


update()
curdoc()
curdoc().add_root(column(inputtabs,
                         textrowob,selectrowob,textrowres,selectrowres,selectrowpres,
                         plottabs,width=pagewidth))

"""
from func.funcAVOModels import *
from data.structLith import structLith, structAVOMod
from avoPyConfig import *
from templates.plots import *

import bokeh.layouts as bkl
import bokeh.plotting as bkp
import bokeh.models as bkm


bkp.output_file('avo_test.html',mode='inline')

for lith in lithAr:
    lith.calcModel(nsim,std,nvar)
    
source = bkm.ColumnDataSource(dict(
            name=[ln.name for ln in lithAr],
            colour=[ln.colour for ln in lithAr],
            vp=[ln.Vp for ln in lithAr],
            vs=[ln.Vs for ln in lithAr],
            rho=[ln.Rho for ln in lithAr],
            vp_std=[ln.VpStd for ln in lithAr],
            vs_std=[ln.VsStd for ln in lithAr],
            rho_std=[ln.RhoStd for ln in lithAr]))

intfMod=[]    
for intf in intfAr:
    intfMod.append(structAVOMod(intf[0],intf[1],nsim,std,nvar,intf[2]))

pAVO=plotAVO(TOOLS,intfMod)
pRPRS=plotRPRS(TOOLS,intfMod)
pAIVPVS=plotAIVPVS(TOOLS,lithAr)
pLMR=plotLMR(TOOLS,lithAr)
p = bkl.gridplot([[pAVO,pRPRS],[pLMR,pAIVPVS]])


#toggle boxes
#intfnames=[i.name for i in intfMod]; actNames=[i for i in range(len(intfnames))]
#toggleIntf = CheckboxGroup( labels=intfnames,active=actNames)
#titleIntf = PreText(text='Interfaces')

#q = VBox(titleIntf,toggle)


columns = [
        bkw.TableColumn(field="name", title="Unit"),
        bkw.TableColumn(field="colour",title="Colour"),
        bkw.TableColumn(field="vp", title="Velp"),
        bkw.TableColumn(field="vs", title="Vels"),
        bkw.TableColumn(field="rho", title="Rho"),
        bkw.TableColumn(field="vp_std", title="Velp_Std"),
        bkw.TableColumn(field="vs_std", title="Vels_Std"),
        bkw.TableColumn(field="rho_std", title="Rho_Std"),
    ]
data_table = bkw.DataTable(source=source, columns=columns, width=1500, height=500,editable=True)

#tab1 = Panel(HBox(q,p))
tab1 = bkw.Panel(child=p,title='Plots')
tab2 = bkw.Panel(child=data_table,title='Parameters')

#curdoc().add_root(HBox(q,p))
tabs = bkw.Tabs(tabs = [tab1,tab2])

#x=calcRandNorm(3660,135,0.77,0.05)
#print(x)
#y=calcRandNorm(3660,135,np.random.rand(10),0.05)
#print(y)
bkp.show(tabs)

#bkp.show(p)




# create a plot and style its properties
p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
p.border_fill_color = 'black'
p.background_fill_color = 'black'
p.outline_line_color = None
p.grid.grid_line_color = None

# add a text renderer to our plot (no data yet)
r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="20pt",
           text_baseline="middle", text_align="center")

i = 0

ds = r.data_source

# create a callback that will add a number in a random location
def callback():
    global i

    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random()*70 + 15]
    new_data['y'] = ds.data['y'] + [random()*70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
    new_data['text'] = ds.data['text'] + [str(i)]
    ds.data = new_data

    i = i + 1

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))

"""
###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 22-9-2018

# File Name: dims.py

# Synopsis:
# Class to handle interactive selection of data models in geopy.
# DIMS - Data Input Manager & Selector

###############################################################################

from collections import OrderedDict

class ExtOrderedDict(OrderedDict):

    def __init__(self):
        super(ExtOrderedDict,self).__init__()

    def keyslist(self):
        return list(self.keys())

import numpy as np
import pandas as pd

from bokeh.layouts import row, column
from bokeh.models import TableColumn, DataTable, ColumnDataSource, Panel, Tabs
from bokeh.models.widgets import Slider, Select, Div

from data.structLith import structRock, structMineral, structFluid, structDryFrame
#from func.funcRP import calcDryFrame_dPres, calcVelp, calcVels, gassmann_dry2fluid, mixfluid

class widgetDIMS(object):

    column_names_rocks = ['kclay', 'muclay', 'rhoclay',
                          'knonclay', 'munonclay', 'rhononclay',
                          'vclay', 'phi', 'dryEk', 'dryPk', 'dryEg', 'dryPg']
    column_names_fluids = ['Name', 'ko', 'rhoo', 'kw', 'rhow', 'kg', 'rhog', 'so', 'sw', 'sg'   ]
    column_names_pres = ['Name', 'OB_Grad', 'init_Pres', 'curr_Pres']
    column_names_output = ['rock', 'fluid', 'Vp', 'Vs', 'rho', 'other']

    def __init__(self,init_depth,file_rocks,file_fluids,file_prespfs,fdi=None):
        '''
        :param init_depth: Initial depth to model (TVDSS).
        :param file_rocks: File with input mineral parameters.
        :param file_fluids: File with input fluid parameters.
        :param file_prespfs: File with input pressure profiles.
        :keyword dependents: A list of geoPy widgets which need to be updated when widgetDIMS is changed.
        '''
        # Initial Data
        self.df_rocks = pd.read_csv(file_rocks, skipinitialspace=True)
        self.df_fluids = pd.read_csv(file_fluids, skipinitialspace=True)
        self.df_pres = pd.read_csv(file_prespfs, skipinitialspace=True)
        self.init_depth = init_depth  # mTVDSS
        self.pagewidth = 1000  # pixels
        self.fdi = fdi

        # Setup Sources
        self.CDS_rocks = ColumnDataSource(self.df_rocks)
        self.CDS_fluids = ColumnDataSource(self.df_fluids)
        self.CDS_pres = ColumnDataSource(self.df_pres)
        self.CDS_out = ColumnDataSource(data=dict())
        # Extract Names
        self.odict_rocks = self.__odictIndex(self.df_rocks.Name.tolist())
        self.odict_fluids = self.__odictIndex(self.df_fluids.Name.tolist())
        self.odict_pres = self.__odictIndex(self.df_pres.Name.tolist())
        # Setup widgets
        self.createTableWidgets()
        self.createControls()
        self.createLayout()

        self.on_selection_change('value',1,1)

    def __odictIndex(self,keys):
        out = ExtOrderedDict()
        for ind,key in enumerate(keys):
            out[key] = ind
        return out

    def createTableWidgets(self):
        self.col_rocks =  [TableColumn(field=Ci, title=Ci) for Ci in self.column_names_rocks]
        self.col_fluids = [TableColumn(field=Ci, title=Ci) for Ci in self.column_names_fluids]
        self.col_pres =   [TableColumn(field=Ci, title=Ci) for Ci in self.column_names_pres]
        self.col_out =    [TableColumn(field=Ci, title=Ci) for Ci in self.column_names_output]
        #Setup table widgets
        tablekwargs = {'width': self.pagewidth, 'editable': True}
        self.TW_rocks =  DataTable(source=self.CDS_rocks,  columns=self.col_rocks,  **tablekwargs)
        self.TW_fluids = DataTable(source=self.CDS_fluids, columns=self.col_fluids, **tablekwargs)
        self.TW_pres =   DataTable(source=self.CDS_pres,   columns=self.col_pres,   **tablekwargs)
        self.TW_out =    DataTable(source=self.CDS_out,    columns=self.col_out,    **tablekwargs)

    def createControls(self):
        # Setup Select Panes and Input Widgets

        #Obr - Overburden rock  #ResR - Reservoir rock
        #Obf - Oberburden fluid #Resf - Reservoir fluid
        self.selectObr = Select(value=self.odict_rocks.keyslist()[0], options=self.odict_rocks.keyslist(),
                                title="Rock  Model")
        self.selectResR = Select(value=self.odict_rocks.keyslist()[0], options=self.odict_rocks.keyslist(),
                                 title="Rock  Model")
        self.selectObf = Select(value=self.odict_fluids.keyslist()[0], options=self.odict_fluids.keyslist(),
                                title="Fluid Model")
        self.selectResf = Select(value=self.odict_fluids.keyslist()[0], options=self.odict_fluids.keyslist(),
                                 title="Fluid Model")
        self.selectPres = Select(value=self.odict_pres.keyslist()[0], options=self.odict_pres.keyslist(),
                                 title="Pressure Scenario")

        self.slideDepth = Slider(start=0, end=10000, value=self.init_depth, step=10, title='Depth (TVDSS)',
                                 callback_policy='mouseup')

        self.selectObr.on_change('value', self.on_selection_change)
        self.selectResR.on_change('value', self.on_selection_change)
        self.selectObf.on_change('value', self.on_selection_change)
        self.selectResf.on_change('value', self.on_selection_change)
        self.selectPres.on_change('value', self.on_selection_change)
        self.slideDepth.on_change('value', self.on_selection_change)

    def createLayout(self):
        # Layout of Page
        self.inputTab1 = Panel(child=self.TW_rocks,  title='Rock Models')
        self.inputTab2 = Panel(child=self.TW_fluids, title='Fluid Mixes')
        self.inputTab3 = Panel(child=self.TW_pres,   title='Pressure Scenarios')
        self.inputTab4 = Panel(child=self.TW_out,    title='Model Calculations')

        self.inputTabs = Tabs(tabs=[self.inputTab1, self.inputTab2,
                                    self.inputTab3, self.inputTab4],
                                    width=self.pagewidth, height=200)

        textrowob = Div(text="<h1> Overburden: </h1>")
        selectrowob = row(self.selectObr, self.selectObf, width=500, height=50, sizing_mode="scale_both")
        textrowres = Div(text="<h1> Reservoir: </h1>")
        selectrowres = row(self.selectResR, self.selectResf, width=500, height=50, sizing_mode="scale_both")
        selectrowpres = row(self.selectPres, self.slideDepth, width=500, height=50, sizing_mode="scale_both")
        self.layout = column(self.inputTabs,
                             textrowob,
                             selectrowob,
                             textrowres,
                             selectrowres,
                             selectrowpres, width=self.pagewidth)

    def on_selection_change(self,attribute,old,new):
        # update active selections
        self.activeObr =  self.df_rocks.loc[self.odict_rocks[self.selectObr.value]]     #Overburden Rock and Fluid
        self.activeObf =  self.df_fluids.loc[self.odict_fluids[self.selectObf.value]]
        self.activeResR = self.df_rocks.loc[self.odict_rocks[self.selectResR.value]]    #Reservoir Rock and Fluid
        self.activeResF = self.df_fluids.loc[self.odict_fluids[self.selectResf.value]]
        self.activePresPf = self.df_pres.loc[self.odict_pres[self.selectPres.value]]  #Pressure Profile
        self.cur_depth = self.slideDepth.value
        self.updateRocks()
        self.updateFluids()
        self.updateRockModel()
        if self.fdi != None:
            self.fdi.updateModel(self.activeResR_dry, self.activeResF_mix, self.fdi.min_pres, self.fdi.max_pres,
                                 init_imp=self.activeResRM.pimp)

    def updateRocks(self):
        #update rock models based upon selections
        parnonclay = ['knonclay', 'munonclay', 'rhononclay'];
        parclay = ['kclay', 'muclay', 'rhoclay']
        obnonshale = structMineral('nonshale', *[self.activeObr[par] for par in parnonclay])
        obshale = structMineral('shale', *[self.activeObr[par] for par in parclay])
        nonshale = structMineral('nonshale', *[self.activeResR[par] for par in parnonclay])
        shale = structMineral('shale', *[self.activeResR[par] for par in parclay])
        # output rock names to table
        self.CDS_out.data['rock'] = [self.activeObr['Name'], self.activeResR['Name']]

        #update dryrock properties
        self.activeObr_dry = structDryFrame(self.activeObr['Name'], obnonshale, obshale, self.activeObr['vclay'],
                                   self.activeObr['phi'])
        self.activeResR_dry = structDryFrame(self.activeResR['Name'], nonshale, shale, self.activeResR['vclay'],
                                    self.activeResR['phi'])
        self.activeObr_dry.calcRockMatrix(); self.activeResR_dry.calcRockMatrix()
        parp = ['init_Pres', 'curr_Pres']; pardry = ['dryEk', 'dryPk', 'dryEg', 'dryEk']
        self.activeObr_dry.calcDryFrame(self.activePresPf['OB_Grad'], self.cur_depth, *[self.activePresPf[par] for par in parp],
                               *[self.activeObr[par] for par in pardry])
        self.activeResR_dry.calcDryFrame(self.activePresPf['OB_Grad'], self.cur_depth, *[self.activePresPf[par] for par in parp],
                                *[self.activeResR[par] for par in pardry])

    def updateFluids(self):
        # oil, water, gas, setup and mixing
        parw = ['kw', 'rhow', 'sw']; paro = ['ko', 'rhoo', 'so']; parg = ['kg', 'rhog', 'sg']
        self.activeObf_mix = structFluid(self.activeObf['Name'], water=[self.activeObf[ind] for ind in parw],
                                                         oil=[self.activeObf[ind] for ind in paro],
                                                         gas=[self.activeObf[ind] for ind in parg])
        self.activeResF_mix = structFluid(self.activeResF['Name'], water=[self.activeResF[ind] for ind in parw],
                                                           oil=[self.activeResF[ind] for ind in paro],
                                                           gas=[self.activeResF[ind] for ind in parg])
        # output fluid names to table
        self.CDS_out.data['fluid'] = [self.activeObf['Name'], self.activeResF['Name']]


    def updateRockModel(self):

        # calculate rock models and properties
        self.activeObrM = structRock(self.activeObr_dry, self.activeObf_mix)
        self.activeObrM.calcGassmann(); self.activeObrM.calcDensity(); self.activeObrM.calcElastic()
        self.activeResRM = structRock(self.activeResR_dry, self.activeResF_mix)
        self.activeResRM.calcGassmann(); self.activeResRM.calcDensity(); self.activeResRM.calcElastic()

        # output rockproperties to table
        self.CDS_out.data['Vp'] = [self.activeObrM.velp, self.activeResRM.velp]
        self.CDS_out.data['Vs'] = [self.activeObrM.vels, self.activeResRM.vels]
        self.CDS_out.data['rho'] = [self.activeObrM.den, self.activeResRM.den]
        self.CDS_out.data['other'] = [self.activeObrM.pimp, self.activeResRM.pimp]

if __name__ == "__main__":
    from os.path import dirname, join, split
    from os import getcwd
    from bokeh.io import show

    #setup figure variables
    idepth = 3180  # mTVDSS

    print('before')
    if split(getcwd())[-1] == 'layouts':
        inputs = join('..','inputs')
    elif split(getcwd())[-1] == 'geoPy':
        inputs = 'inputs'
    else:
        raise SystemError
        print("Can't run from this file from: "+getcwd())

    print('after')
    fr = join(dirname(__file__),inputs,'geoPy_rocks.csv')
    ff = join(dirname(__file__),inputs,'geoPy_fluids.csv')
    fp = join(dirname(__file__),inputs,'geoPy_pres.csv')

    dims = widgetDIMS(idepth,fr,ff,fp)
    show(dims.TW_rocks)







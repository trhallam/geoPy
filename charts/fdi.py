###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 20-9-2018

# File Name: fdi.py

# Synopsis:
# Class to handle interactive plotting in bokeh of 4D impedance changes related
# changes in saturation and pressure.

# Adapted from original fourdimp.py to be a class structure to enable interactions.

###############################################################################

import numpy as np
from colorcet import b_diverging_bwr_40_95_c42

from bokeh.layouts import row, column
from bokeh.models import LayoutDOM, LinearColorMapper, ColorBar, ColumnDataSource
from bokeh.models.widgets import Slider, RadioButtonGroup, Button
from bokeh.plotting import figure

from data.structLith import structRock
from func.funcRP import calcDryFrame_dPres, calcVelp, calcVels, gassmann_dry2fluid, mixfluid

import random

#global variables for charting and data control

class widgetFDI(object):

    mesh_keys = ['image', 'mesh_sw', 'mesh_so', 'mesh_sg', 'mesh_pres', 'mesh_dryk', 'mesh_dryg', 'mesh_pimp', 'mesh_dpimp']
    vec_keys  = ['sw', 'so', 'sg', 'swso', 'pres', 'dimpcsat', 'dimpcpres', 'ipres', 'isw', 'cpres', 'csw']
    patch_keys = ['psw','pso','psg','ysw','yhyd']

    def __init__(self,plot_scale,min_pres,max_pres):
        '''
        :param plot_scale: number of samples for mesh ploting [plot_scale x plot_scale]
        '''
        #dump external variables
        self.min_pres = min_pres
        self.max_pres = max_pres
        self.cur_pres = 0; self.cur_sat=0
        self.plot_scale = plot_scale

        #control defaults
        self.toggleAbs = False

        # create data templates and dictionaries
        self.mesh = [np.empty([plot_scale, plot_scale])]
        self.mesh_dict = dict()
        self.vec = np.empty(plot_scale)
        self.vec_dict = dict()
        self.patch = np.empty(3)
        self.patch_dict = dict()
        for mk in self.mesh_keys:
            self.mesh_dict[mk] = self.mesh
        for vk in self.vec_keys:
            self.vec_dict[vk] = self.vec
        for pk in self.patch_keys:
            self.patch_dict[pk] = self.patch

        self.patch_dict['ysw'] = [0,1,1]; self.patch_dict['yhyd'] = [0,1,0]

        self.CDS_mesh = ColumnDataSource(self.mesh_dict)
        self.CDS_vec = ColumnDataSource(self.vec_dict)
        self.CDS_pat = ColumnDataSource(self.patch_dict)

        self.createChartDImp()
        self.createChartSat()
        self.createChartCPresDImp()
        self.createChartCSatDImp()
        self.createControls()
        self.createLayout()

    def createChartDImp(self):
        self.figDImp = figure(title="Delta Impedance for Pres vs Saturation", tools="hover,wheel_zoom,pan,reset",
                              tooltips=[("Pres (MPa)", "$x"), ("Sw (frac)", "$y"), ("dImp (%)", "@image"),
                              ("So", "@mesh_so{0.2f}"), ("Sg", "@mesh_sg{0.2f}"), ("Pres", "@mesh_pres")],
                              x_range=(self.min_pres, self.max_pres), y_range=(0, 1))
        self.figDImp.xaxis.axis_label = "Reservoir Pressure (MPa)"
        self.figDImp.yaxis.axis_label = "Water Saturation (Frac)"
        self.dicm = LinearColorMapper(palette=b_diverging_bwr_40_95_c42, low=-5, high=5)
        # must give a vector of image data for image parameter
        self.figDImp.image(source=self.CDS_mesh,image='image', x=self.min_pres, y=0, dw=self.max_pres - self.min_pres,
                           dh=1, color_mapper=self.dicm)
        self.figDImp_color_bar = ColorBar(color_mapper=self.dicm, bar_line_color='black', label_standoff=12,
                             major_tick_line_color = 'black', border_line_color=None, location=(0, 0))
        self.figDImp.add_layout(self.figDImp_color_bar, 'right')

        self.figDImp.line('pres','csw',source=self.CDS_vec,color='black',alpha=0.8)
        self.figDImp.line('cpres','sw',source=self.CDS_vec,color='black',alpha=0.8)

    def createChartSat(self):
        self.figSat = figure(title='Saturation',x_range=(0, 1),y_range=(0, 1),width=250)
        self.figSat.xaxis.axis_label = "frac"
        self.figSat.yaxis.axis_label = "frac"
        self.satColours = ['#4286f4', '#2fbc36', '#e8372e']

        self.figSat.patch(y='ysw',x='psw',source=self.CDS_pat,color=self.satColours[0],alpha=0.75)
        self.figSat.patch(y='yhyd',x='pso',source=self.CDS_pat,color=self.satColours[1],alpha=0.75)
        self.figSat.patch(y='yhyd',x='psg',source=self.CDS_pat,color=self.satColours[2],alpha=0.75)

        self.figSat.line('sw','sw',source=self.CDS_vec,color='black')
        self.figSat.line('swso','sw',source=self.CDS_vec,color='black')

    def createChartCSatDImp(self):
        self.figCSat = figure(title='Constant Saturation vs Delta Imp',height=300)
        self.figCSat.xaxis.axis_label = "Pressure (MPa)"
        self.figCSat.yaxis.axis_label = "Delta Imp (%)"
        self.figCSat.line('pres','dimpcsat',source=self.CDS_vec,color='black')

    def createChartCPresDImp(self):
        self.figCPres = figure(title='Constant Pressure vs Delta Imp',height=300)
        self.figCPres.xaxis.axis_label = "Saturation Sw (frac)"
        self.figCPres.yaxis.axis_label = "Delta Imp (%)"
        self.figCPres.line('sw','dimpcpres',source=self.CDS_vec,color='black')

    def createControls(self):
        delta_pres = (self.max_pres - self.min_pres)/(self.plot_scale-1)
        delta_sat = 1.0 / (self.plot_scale - 1)
        self.slidePres = Slider(start=self.min_pres, end=self.max_pres,
                                value=self.min_pres+(self.max_pres-self.min_pres),
                                step=delta_pres, title= 'Constant Pressure')
        self.slideSat = Slider(start=0, end=1, value=0.5, step=delta_sat, title= 'Constant Saturation')
        self.radioAbsRel = RadioButtonGroup(labels=['Absolute','Relative'], active=1)
        self.buttonReset = Button(label='Reset Initial Conditions')

        self.slidePres.on_change('value',self.updateCPres)
        self.slideSat.on_change('value',self.updateCSat)
        self.radioAbsRel.on_change('active',self.toggleAbsRel)

    def createLayout(self):
        controls_row = row(self.slidePres,self.slideSat,self.radioAbsRel, self.buttonReset)
        plots_row = row(self.figSat,self.figDImp,column(self.figCSat,self.figCPres))
        self.layout = column(controls_row,plots_row)

    def updateCImpAndSat(self):#, pres, sat):
        '''
        Updates Impedance for constant saturation.
        :param pres: Constant pressure to extract along.
        :param sat:  Constant saturation to extract along.
        '''
        ipres = np.argwhere(self.vec_dict['pres'] >= self.cur_pres)[0][0]
        isat = np.argwhere(self.vec_dict['sw'] >= self.cur_sat)[0][0]
        ar_cpres = self.vec_dict['cpres']*0+self.vec_dict['pres'][ipres]
        ar_csat = self.vec_dict['csw']*0+self.vec_dict['sw'][isat]
        self.CDS_vec.data['cpres'] = ar_cpres.tolist(); self.CDS_vec.data['csw'] = ar_csat.tolist()
        self.CDS_vec.data['dimpcpres'] = self.mesh_dict['image'][:,ipres].tolist()
        self.CDS_vec.data['dimpcsat'] = self.mesh_dict['image'][isat,:].tolist()

    def updateModel(self, resdryframe, resfluid, presmin, presmax, init_imp=None):
        '''
        :param resdryframe: A dryframe rock model from structLith
        :param resfluid:    A fluid model from structLith
        :type presmin, presmax: Minimum and maximum pressure range to calculate over.
        :keyword init_imp: The initial impedance of the rock. Of None the absolute impedance will be plotted.
        '''

        #extract variables from models
        self.init_pres = resdryframe.resp
        Km_vrh = resdryframe.Km_vrh; Gm_vrh = resdryframe.Gm_vrh
        Ek, Pk, Eg, Pg = resdryframe.mod

        # setup pressure variations
        self.dpres = (presmax - presmin)/(self.plot_scale-1)
        self.vec_dict['pres'] = np.arange(presmin,presmax+self.dpres,self.dpres)

        #setup water saturation variations
        kw, ko, kg = resfluid.getKs(); rhow, rhoo, rhog = resfluid.getRhos(); swi, soi, sgi = resfluid.getSats()
        self.init_sw = swi
        pc_hyd_oil = soi / (1-swi); pc_hyd_gas = sgi / (1-swi)  #work out oil and gas pc
        dsw = 1.0 / (self.plot_scale - 1)                       # delta sw for plotting
        self.vec_dict['sw'] = np.arange(0, 1 + dsw, dsw)        # saturation water

        #update patches
        self.patch_dict['psw']=[0,1,0]; self.patch_dict['pso']=[0,1,1-pc_hyd_gas]; self.patch_dict['psg']=[1-pc_hyd_gas,1,1]

        #create meshes
        self.mesh_dict['mesh_pres'], self.mesh_dict['mesh_sw'] = np.meshgrid(self.vec_dict['pres'], self.vec_dict['sw'])
        self.mesh_dict['mesh_so'] = (1.-self.mesh_dict['mesh_sw'])*pc_hyd_oil             #saturation oil
        self.mesh_dict['mesh_sg'] = (1.-self.mesh_dict['mesh_sw'])*pc_hyd_gas             #saturation gas
        self.vec_dict['so'] = self.mesh_dict['mesh_so'][:,0]; self.vec_dict['sg'] = self.mesh_dict['mesh_sg'][:,0]
        self.vec_dict['swso'] = 1-(self.vec_dict['sg'])     #saturation oil and water frac for plotting

        mesh_mfluidK = np.empty(self.mesh_dict['mesh_sw'].shape)
        mesh_mfluidRho = np.empty(self.mesh_dict['mesh_sw'].shape)
        for i,row in enumerate(self.mesh_dict['mesh_sw']):
            for j, val in enumerate(row):
                mesh_mfluidK[i,j], mesh_mfluidRho[i,j] = mixfluid(water=[kw,rhow,self.mesh_dict['mesh_sw'][i,j]],
                                                                  oil=[ko,rhoo,self.mesh_dict['mesh_so'][i,j]],
                                                                  gas=[kg,rhog,self.mesh_dict['mesh_sg'][i,j]])
        #calculate rockmodels
        self.mesh_dict['mesh_dryk'] = calcDryFrame_dPres(self.init_pres, self.mesh_dict['mesh_pres'],
                                                         Km_vrh, Ek, Pk, resdryframe.phi, c=resdryframe.c)
        self.mesh_dict['mesh_dryg'] = calcDryFrame_dPres(self.init_pres, self.mesh_dict['mesh_pres'],
                                                         Gm_vrh, Eg, Pg, resdryframe.phi, c=resdryframe.c)

        mesh_satk = gassmann_dry2fluid(self.mesh_dict['mesh_dryk'],Km_vrh,mesh_mfluidK,resdryframe.phi)
        mesh_rhob = resdryframe.rho + mesh_mfluidRho*resdryframe.phi
        self.mesh_dict['mesh_pimp'] = calcVelp(mesh_satk, self.mesh_dict['mesh_dryg'], mesh_rhob) * mesh_rhob
        self.mesh_dict['mesh_dpimp'] = 100.0 * (self.mesh_dict['mesh_pimp'] - init_imp)/init_imp

        self.toggleAbsRel('active',1,1)

        for key in self.mesh_keys:
            self.CDS_mesh.data[key] = [self.mesh_dict[key].tolist()]
        for key in self.vec_keys:
            self.CDS_vec.data[key] = self.vec_dict[key].tolist()
        for key in self.patch_keys:
            self.CDS_pat.data[key] = self.patch_dict[key]

        print(self.patch_dict)
        self.cur_pres = self.init_pres; self.cur_sat = self.init_sw
        self.updateCImpAndSat()

    def toggleAbsRel(self,attribute,old,new):
        print(attribute,old,new)
        if new == 0:
            self.toggleAbs = True
        if new == 1:
            self.toggleAbs = False

        if self.toggleAbs:
            self.mesh_dict['image'] = self.mesh_dict['mesh_pimp']
            self.figCPres.yaxis.axis_label = "Impedance"
            self.figCSat.yaxis.axis_label = "Impedance"
        else:
            self.mesh_dict['image'] = self.mesh_dict['mesh_dpimp']
            self.figCPres.yaxis.axis_label = "Delta Imp (%)"
            self.figCSat.yaxis.axis_label = "Delta Imp (%)"

        #self.figCPres.update()
        #self.figCSat.update()
        self.CDS_mesh.data['image']= [self.mesh_dict['image'].tolist()]
        self.updateCImpAndSat()

    def updateCPres(self,attribute,old,new):
        self.cur_pres=new
        self.updateCImpAndSat()

    def updateCSat(self,attribute,old,new):
        self.cur_sat=new
        self.updateCImpAndSat()

if __name__ == "__main__":

    from data.structLith import structDryFrame, structRock, structFluid, structMineral
    from bokeh.io import show

    #setup figure variables
    idepth = 3180  # mTVDSS
    pagewidth = 1000  # pixels
    presmin = 9; presmax = 15;
    plot_scale = 100

    #setup test data variables
    NameR, kclay, muclay, rhoclay, knonclay, munonclay, rhononclay, vclay, phi, dryEk, dryPk, dryEg, dryPg = \
    ['CV',   15,      5,    2.68,       70,        35,       2.74,  0.05, 0.2,   1.8,    12,    25,     8]
    NameF,       ko,  rhoo,   kw,  rhow,    kg,  rhog,   so,   sw, sg = \
    ['OW_IV', 0.636, 0.686, 2.96, 1.056, 0.017, 0.145, 0.57, 0.33,  0.10]
    NameP, OB_Grad, init_Pres, curr_Pres = ['Default', 0.02262, 12, 12]

    minclay = structMineral(NameR+'_clay',kclay,muclay,rhoclay)
    minnonclay = structMineral(NameR+'_nonclay',knonclay,munonclay,rhononclay)
    fluid = structFluid(NameF,water=[kw,rhow,sw],oil=[ko,rhoo,so],gas=[kg,rhog,sg])
    dryframe = structDryFrame(NameR+'_'+NameF,minnonclay,minclay,vclay,phi)
    dryframe.calcRockMatrix(); dryframe.calcDryFrame(OB_Grad,idepth,init_Pres,curr_Pres,dryEk,dryPk,dryEg,dryPg)
    rock = structRock(dryframe,fluid)
    rock.calcGassmann(), rock.calcDensity(), rock.calcElastic()

    #data_mesh, data_vec = createDataTables(plot_scale)
    #fdi_layout = layoutDImp(data_mesh,data_vec,presmin,presmax,init_Pres,sw,plot_scale)
    fdi = widgetFDI(plot_scale, presmin, presmax)
    fdi.updateModel(dryframe,fluid,presmin,presmax,init_imp=rock.pimp)
    #update_c_imp_sat(data_mesh,data_vec,init_Pres,sw)

    show(fdi.layout)







###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 12-9-2018

# File Name: fourdimp.py

# Synopsis:
# Calculate change in impedance for a rock as a function of pressure and
# saturation changes. Plot to image type in bokeh.

###############################################################################

import numpy as np
from colorcet import b_diverging_bwr_40_95_c42

from bokeh.layouts import row, column
from bokeh.models import LinearColorMapper, ColorBar, ColumnDataSource
from bokeh.models.widgets import Slider, Button
from bokeh.plotting import figure

from data.structLith import structRock
from func.funcRP import calcDryFrame_dPres, calcVelp, calcVels, gassmann_dry2fluid, mixfluid

import random

#global variables for charting and data control

fdi_mesh_keys = ['image', 'mesh_sw', 'mesh_so', 'mesh_sg', 'mesh_pres', 'mesh_dryk', 'mesh_dryg']
fdi_vec_keys   = ['sw', 'so', 'sg', 'swso', 'pres', 'dimpcsat', 'dimpcpres', 'ipres', 'isw', 'cpres', 'csw']

def createDataTables(plot_scale):
    '''
    Creates the data tables needed by this module using bokeh models so that charts can be interactively updated.
    :param plot_scale: number of samples for mesh ploting [plot_scale x plot_scale]
    :return: A bokeh data table model.
    '''
    xy = plot_scale + 1
    # create data templates and dictionaries
    fdi_mesh = [np.empty([plot_scale, plot_scale])]; fdi_mesh_dict = dict();
    fdi_vec = np.empty(plot_scale); fdi_vec_dict = dict()
    for mk in fdi_mesh_keys:
        fdi_mesh_dict[mk] = fdi_mesh
    for vk in fdi_vec_keys:
        fdi_vec_dict[vk] = fdi_vec
    #return bokeh column data source models
    return ColumnDataSource(fdi_mesh_dict), ColumnDataSource(fdi_vec_dict)

def chartDImp(fdi_mesh,fdi_vec, presmin, presmax):
    '''
    Creates the delta impedance figure
    :param fdi_mesh: the mesh data table from createDataTables
    :param fdi_vec: the vector data table from createDataTables
    :param presmin: minimum pressure to plot
    :param presmax: maximum pressure to plot
    :return:
    '''
    fig = figure(title="Delta Impedance for Pres vs Saturation", tools="hover,wheel_zoom,pan,reset",
           tooltips=[("Pres (MPa)", "$x"), ("Sw (frac)", "$y"), ("dImp (%)", "@image"),
                     ("So", "@mesh_so{0.2f}"), ("Sg", "@mesh_sg{0.2f}"), ("Pres", "@mesh_pres")],
           x_range=(presmin, presmax), y_range=(0, 1))
    fig.xaxis.axis_label = "Reservoir Pressure (MPa)"
    fig.yaxis.axis_label = "Water Saturation (Frac)"
    dicm = LinearColorMapper(palette=b_diverging_bwr_40_95_c42, low=-5, high=5)
    # must give a vector of image data for image parameter
    fig.image(source=fdi_mesh,image='image', x=presmin, y=0, dw=presmax - presmin, dh=1, color_mapper=dicm)
    color_bar = ColorBar(color_mapper=dicm, bar_line_color='black', label_standoff=12,
                         major_tick_line_color = 'black', border_line_color=None, location=(0, 0))
    fig.add_layout(color_bar, 'right')

    fig.line('pres','csw',source=fdi_vec,color='black',alpha=0.8)
    fig.line('cpres','sw',source=fdi_vec,color='black',alpha=0.8)
    return fig

def chartSat(data):
    fig = figure(title='Saturation',x_range=(0, 1),y_range=(0, 1),width=250)
    fig.xaxis.axis_label = "frac"
    fig.yaxis.axis_label = "frac"
    colours = ['#4286f4', '#2fbc36', '#e8372e']
    fig.line('sw','sw',source=data,color='black')
    fig.line('sw','swso',source=data,color='black')
    return fig

def chartcSatDImp(data):
    fig = figure(title='Constant Saturation vs Delta Imp',height=300)
    fig.xaxis.axis_label = "Pressure (MPa)"
    fig.yaxis.axis_label = "Delta Imp (%)"
    fig.line('pres','dimpcsat',source=data,color='black')
    return fig

def chartcPresDImp(data):
    fig = figure(title='Constant Pressure vs Delta Imp',height=300)
    fig.xaxis.axis_label = "Saturation Sw (frac)"
    fig.yaxis.axis_label = "Delta Imp (%)"
    fig.line('sw','dimpcpres',source=data,color='black')
    return fig

def controls_c_imp_sat(i_pres,min_pres,max_pres,i_sat,plot_scale):
    delta_pres = (max_pres - min_pres)/(plot_scale-1)
    delta_sat = 1.0 / (plot_scale - 1)
    slide_pres = Slider(start=min_pres, end=max_pres, value=i_pres, step=delta_pres, title= 'Constant Pressure')
    slide_sat = Slider(start=0, end=1, value=i_sat, step=delta_sat, title= 'Constant Pressure')
    button_reset = Button(label='Reset Initial Conditions')



    return slide_pres, slide_sat, button_reset

def layoutDImp(fdi_mesh,fdi_vec, presmin, presmax, i_pres, i_sat, plot_scale):
    '''

    :param fdi_mesh: the mesh data source created by fourdimp.createDataTables
    :param fdi_vec: the vector data source created by fourdim.createDataTables
    :return: bokeh panel to be used in geoPy or stand alone.
    '''
    fdi_sat_fig = chartSat(fdi_vec)
    fdi_imp_fig = chartDImp(fdi_mesh, fdi_vec, presmin, presmax)
    fdi_csat_fig = chartcSatDImp(fdi_vec)
    fdi_cpres_fig = chartcPresDImp(fdi_vec)
    fdi_cpres_slide, fdi_csat_slide, fdi_reset_button = controls_c_imp_sat(i_pres, presmin, presmax, i_sat, plot_scale)

    return row(column(row(fdi_cpres_slide,fdi_csat_slide,fdi_reset_button),row(fdi_sat_fig, fdi_imp_fig)),
               column(fdi_csat_fig, fdi_cpres_fig))
    #return Panel(child=fdi_csat_fig,width=1000)

def update_c_imp_sat(fdi_mesh, fdi_vec, pres, sat):
    '''
    Updates Impedance for constant saturation.
    :param pres: Constant pressure to extract along.
    :param sat:  Constant saturation to extract along.
    '''
    ipres = np.argwhere(np.array(fdi_vec.data['pres']) >= pres)[0][0]
    isat = np.argwhere(np.array(fdi_vec.data['sw']) >= sat)[0][0]
    ar_cpres = np.array(fdi_vec.data['cpres'])*0+fdi_vec.data['pres'][ipres]
    ar_csat = np.array(fdi_vec.data['csw'])*0+fdi_vec.data['sw'][isat]
    fdi_vec.data['cpres'] = ar_cpres.tolist(); fdi_vec.data['csw'] = ar_csat.tolist()
    fdi_vec.data['dimpcpres'] = np.array(fdi_mesh.data['image'][0])[:,ipres].tolist()
    fdi_vec.data['dimpcsat'] = np.array(fdi_mesh.data['image'][0])[isat,:].tolist()

def calcDImp(fdi_mesh, fdi_vec, plot_scale, resdryframe, resfluid, presmin, presmax, init_imp):
    '''

    :type init_imp:
    :param bkfig: a bokeh figure pane to populate
    :param rockmodel: a rock model to create the data from
    :return:
    '''
    mkeys = ['image', 'mesh_sw', 'mesh_so', 'mesh_sg', 'mesh_pres', 'mesh_dryk', 'mesh_dryg']
    vkeys = ['sw', 'so', 'sg', 'swso', 'pres', 'dimpcsat', 'dimpcpres','csw','cpres']
    ddict = dict()
    for key in mkeys:
        ddict[key] = fdi_mesh.data[key][0]
    for key in vkeys:
        ddict[key] = fdi_vec.data[key]

    #extract variables from models
    ipres = resdryframe.resp
    Km_vrh = resdryframe.Km_vrh; Gm_vrh = resdryframe.Gm_vrh
    Ek, Pk, Eg, Pg = resdryframe.mod
    phi = resdryframe.phi

    # setup pressure variations
    dpres = (presmax - presmin)/(plot_scale-1)
    ddict['pres'] = np.arange(presmin,presmax+dpres,dpres)

    #setup water saturation variations
    kw, ko, kg = resfluid.getKs(); rhow, rhoo, rhog = resfluid.getRhos(); swi, soi, sgi = resfluid.getSats()
    pc_hyd_oil = soi / (1-swi); pc_hyd_gas = sgi / (1-swi)  #work out oil and gas pc
    dsw = 1.0 / (plot_scale - 1)                     # delta sw for plotting
    ddict['sw'] = np.arange(0, 1 + dsw, dsw)         # saturation water

    #create meshes
    ddict['mesh_pres'], ddict['mesh_sw'] = np.meshgrid(ddict['pres'], ddict['sw'])
    ddict['mesh_so'] = (1.-ddict['mesh_sw'])*pc_hyd_oil             #saturation oil
    ddict['mesh_sg'] = (1.-ddict['mesh_sw'])-ddict['mesh_so']       #saturation gas
    ddict['so'] = ddict['mesh_so'][:,0]; ddict['sg'] = ddict['mesh_sg'][:,0]
    ddict['swso'] = ddict['sw']-ddict['so']                         #saturation oil and water frac for plotting

    mesh_mfluidK = np.empty(ddict['mesh_sw'].shape); mesh_mfluidRho = np.empty(ddict['mesh_sw'].shape);
    for i,row in enumerate(ddict['mesh_sw']):
        for j, val in enumerate(row):
            mesh_mfluidK[i,j], mesh_mfluidRho[i,j] = mixfluid(water=[kw,rhow,ddict['mesh_sw'][i,j]],
                                                              oil=[ko,rhoo,ddict['mesh_so'][i,j]],
                                                              gas=[kg,rhog,ddict['mesh_sg'][i,j]])
    #calculate rockmodels
    ddict['mesh_dryk'] = calcDryFrame_dPres(ipres, ddict['mesh_pres'], Km_vrh, Ek, Pk, phi, c=resdryframe.c)
    ddict['mesh_dryg'] = calcDryFrame_dPres(ipres, ddict['mesh_pres'], Gm_vrh, Eg, Pg, phi, c=resdryframe.c)

    mesh_satk = gassmann_dry2fluid(ddict['mesh_dryk'],Km_vrh,mesh_mfluidK,resdryframe.phi)
    mesh_rhob = resdryframe.rho + mesh_mfluidRho*resdryframe.phi
    mesh_pimp = calcVelp(mesh_satk, ddict['mesh_dryg'], mesh_rhob) * mesh_rhob
    ddict['image'] = 100.0 * (mesh_pimp - init_imp)/init_imp

    for key in mkeys:
        fdi_mesh.data[key] = [ddict[key].tolist()]
    for key in vkeys:
        fdi_vec.data[key] = ddict[key].tolist()

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
    ['OW_IV', 0.636, 0.686, 2.96, 1.056, 0.017, 0.145, 0.56, 0.44,  0]
    NameP, OB_Grad, init_Pres, curr_Pres = ['Default', 0.02262, 12, 12]

    minclay = structMineral(NameR+'_clay',kclay,muclay,rhoclay)
    minnonclay = structMineral(NameR+'_nonclay',knonclay,munonclay,rhononclay)
    fluid = structFluid(NameF,water=[kw,rhow,sw],oil=[ko,rhoo,so],gas=[kg,rhog,sg])
    dryframe = structDryFrame(NameR+'_'+NameF,minnonclay,minclay,vclay,phi)
    dryframe.calcRockMatrix(); dryframe.calcDryFrame(OB_Grad,idepth,init_Pres,curr_Pres,dryEk,dryPk,dryEg,dryPg)
    rock = structRock(dryframe,fluid)
    rock.calcGassmann(), rock.calcDensity(), rock.calcElastic()

    data_mesh, data_vec = createDataTables(plot_scale)
    fdi_layout = layoutDImp(data_mesh,data_vec,presmin,presmax,init_Pres,sw,plot_scale)

    calcDImp(data_mesh,data_vec,plot_scale,dryframe,fluid,presmin,presmax,rock.pimp)
    update_c_imp_sat(data_mesh,data_vec,init_Pres,sw)

    show(fdi_layout)







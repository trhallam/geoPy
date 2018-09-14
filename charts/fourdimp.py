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
import json
from data.structLith import structRock
from colorcet import b_diverging_bwr_40_95_c42
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.plotting import figure

from func.funcRP import calcDryFrame_dPres, calcVelp, calcVels, gassmann_dry2fluid, mixfluid

import random

def chartDImp(data, presmin, presmax):
    fig = figure(title="Delta Impedance for Pres vs Saturation", tools="hover,wheel_zoom,pan,reset",
           tooltips=[("Pres (GPa)", "$x"), ("Sw (frac)", "$y"), ("dImp (%)", "@image"),
                     ("So", "@mesh_so{0.2f}"), ("Sg", "@mesh_sg{0.2f}"), ("Pres", "@mesh_pres")],
           x_range=(presmin, presmax), y_range=(0, 1))
    fig.xaxis.axis_label = "Reservoir Pressure (GPa)"
    fig.yaxis.axis_label = "Water Saturation (Frac)"
    dicm = LinearColorMapper(palette=b_diverging_bwr_40_95_c42, low=-5, high=5)
    # must give a vector of image data for image parameter
    fig.image(source=data,image='image', x=presmin, y=0, dw=presmax - presmin, dh=1, color_mapper=dicm)
    color_bar = ColorBar(color_mapper=dicm, bar_line_color='black', label_standoff=12,
                         major_tick_line_color = 'black', border_line_color=None, location=(0, 0))
    fig.add_layout(color_bar, 'right')
    return fig

def chartSat(data):
    fig = figure(title='Saturation',x_range=(0, 1),y_range=(0, 1),width=250)
    fig.xaxis.axis_label = "frac"
    fig.yaxis.axis_label = "frac"
    colours = ['#4286f4', '#2fbc36', '#e8372e']
    fig.line(source=data, x='sw', y='so')
    #fig.line(x='swso', y='sw', source=data)
    fig.line([0,1],[1,0])
    return fig

def chartcSatDImp(data):
    fig = figure(title='Constant Saturation Pres vs Delta Imp',height=300)
    fig.xaxis.axis_label = "Pressure (GPa)"
    fig.yaxis.axis_label = "Delta Imp (%)"
    fig.line([0,1000],[1,1])
    return fig

def calcDImp(datasource, plot_scale, resdryframe, resfluid, presmin, presmax, init_imp):
    '''

    :type init_imp:
    :param bkfig: a bokeh figure pane to populate
    :param rockmodel: a rock model to create the data from
    :return:
    '''
    dkeys = ['image', 'mesh_sw', 'mesh_so', 'mesh_sg', 'mesh_pres', 'mesh_dryk', 'mesh_dryg', #mesh keys
             'sw', 'so', 'sg', 'swso', 'pres', 'dimpcsat', 'dimpcpres'] #vector keys
    ddict = dict()
    for key in dkeys:
        ddict[key] = datasource.data[key][0]

    ipres = resdryframe.resp
    Km_vrh = resdryframe.Km_vrh; Gm_vrh = resdryframe.Gm_vrh
    Ek, Pk, Eg, Pg = resdryframe.mod
    phi = resdryframe.phi

    # setup pressure variations
    dpres = (presmax - presmin)/(plot_scale-1)
    ddict['pres'] = np.arange(presmin,presmax+dpres,dpres)
    ddict['mesh_pres'] = np.tile(ddict['pres'],plot_scale).reshape(plot_scale,plot_scale)

    # setup saturation variations
    #i_imp = resrockmodel.pimp

    kw,ko,kg = resfluid.getKs(); rhow,rhoo,rhog = resfluid.getRhos(); swi,soi,sgi = resfluid.getSats()
    #water = resfluid.water; oil = resfluid.oil; gas = resfluid.gas

    ratio_og = soi/sgi; total_og = ratio_og+1        #work out oil-gas ratios
    dsw = 1.0 / (plot_scale-1)                       #delta sw for plotting
    ddict['sw'] = np.arange(0,1+dsw,dsw)             #saturation water
    ddict['so'] = (1.-ddict['sw'])*ratio_og/total_og #saturation oil
    ddict['sg'] = (1.-ddict['sw'])-ddict['so']       #saturation gas
    ddict['swso'] = ddict['sw']+ddict['so']          #saturation oil and water frac for plotting

    # create saturation meshes
    ddict['mesh_sw'] = ddict['sw'].repeat(plot_scale).reshape(plot_scale,plot_scale)
    ddict['mesh_so'] = ddict['so'].repeat(plot_scale).reshape(plot_scale,plot_scale)
    ddict['mesh_sg'] = ddict['sg'].repeat(plot_scale).reshape(plot_scale,plot_scale)

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

    for key in dkeys:
        datasource.data[key] = [ddict[key]]

    file = open('dict.txt', 'w')
    for key in dkeys:
        json.dump(key, file, indent=2)
        json.dump(ddict[key].tolist(), file, indent=1)

    file.close()
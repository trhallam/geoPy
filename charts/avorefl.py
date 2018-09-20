###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 16-9-2018

# File Name: avorefl.py

# Synopsis:
# Caculate and plot the reflectivity with changing incidence angles for two
# rocks in a half space.

###############################################################################

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from bokeh.models.widgets import DataTable, TableColumn, Select, Slider

from func.funcZoep import zoeppritzfull, bortfeld, akirichards, shuey, zoeppritzPray

import numpy as np

def createDataTable(min,max,nang):
    '''
    Creates a data table usking bokeh models so that charts can be interactively updated.
    :param min: Minimum angle to plot.
    :param max: Maximum angle to plot.
    :param nang: Number of angles between but including min and max.
    :return: A bokeh data table model.
    '''
    da = (max-min)/(nang-1)
    ang = np.arange(min,max+da,da);
    #mod = ang.repeat(2).reshape([nang,2])
    mod = np.empty(ang.shape)
    avomodkeys = ['zoepRp','zoepTp','zoepRs','zoepTs',
                  'bortfeldRp',
                  'ar_avsethRp','ar_arRp',
                  'shuey']
    avomoddict = {'ang' : ang}
    for mk in avomodkeys:
        avomoddict[mk] = mod
    return ColumnDataSource(avomoddict)

def updateAVOmod(datatable,vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    Updates the output table of createDataTable AVO models to reflect input
    elastic parameters.
    :param datatable: out of createDataTable, specific for AVO modelling.
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: updates datatable in place
    '''
    avomodkeys = ['zoepRp', 'zoepTp', 'zoepRs', 'zoepTs',
                  'bortfeldRp',
                  'ar_avsethRp','ar_arRp',
                  'shuey']
    ang = np.radians(datatable.data['ang'])
    ldict = dict()
    for mk in avomodkeys: ldict[mk] = np.empty(ang.shape)
    for i,a in enumerate(ang):
        ldict['zoepRp'][i], ldict['zoepTp'][i], ldict['zoepRs'][i], ldict['zoepTs'][i] =\
            zoeppritzPray(a,vp1,vs1,rho1,vp2,vs2,rho2)
        ldict['bortfeldRp'][i] = bortfeld(a,vp1,vs1,rho1,vp2,vs2,rho2)
        ldict['ar_avsethRp'][i] = akirichards(a,vp1,vs1,rho1,vp2,vs2,rho2,method='avseth')
        ldict['ar_arRp'][i] = akirichards(a,vp1,vs1,rho1,vp2,vs2,rho2,method='ar')
        ldict['shuey'][i] = shuey(a,vp1,vs1,rho1,vp2,vs2,rho2)

    for mk in avomodkeys: #update datasource
        datatable.data[mk] = ldict[mk].tolist()

if __name__ == "__main__":
    from numpy import round
    from tests import test_title_msg, test_msg
    from bokeh.io import show
    from bokeh.palettes import Dark2

    from bruges.reflection import zoeppritz as bruges_zp

    # test setup
    thetaid = 20  # degrees
    thetair = 0.349066  # radians
    thetamin = 0; thetamax = 45; N=25
    vp1 = 3000; vs1 = 1800; rho1 = 2.4
    vp2 = 3500; vs2 = 2200; rho2 = 2.55

    test_title_msg('createDataTable')
    act_dataT = createDataTable(thetamin,thetamax,N)
    qcr_dataTab_ang = [ 0.,1.875,3.75,5.625,7.5,9.375,11.25,13.125,15.,16.875,18.75,20.625,22.5,24.375,
                        26.25,28.125,30.,31.875,33.75,35.625,37.5,39.375,41.25,43.125,45.]
    test_msg('createDataTable','Testing Angles',act_dataT.data['ang'],qcr_dataTab_ang)

    updateAVOmod(act_dataT,vp1,vs1,rho1,vp2,vs2,rho2)

    test_fig = figure(y_range=(-0.2,0.2), plot_width=500, x_range=(thetamin, thetamax), toolbar_location=None)
    test_fig.xaxis.axis_label = "Incident Angle (deg)"
    test_fig.yaxis.axis_label = "Reflection Coefficient"
    test_fig.title.text = "Angle vs Amplitude Models"
    fig_line_kwargs = {'source':act_dataT, 'line_width':2, 'alpha':0.8}
    cd2_7=Dark2[7]
    mods = ['zoepRp', 'bortfeldRp', 'ar_avsethRp', 'ar_arRp', 'shuey']
    for name, col in zip(mods,cd2_7):
        test_fig.line('ang',name,line_color=col,legend=" "+name,source=act_dataT,line_width=2,alpha=0.8)

    ang = act_dataT.data['ang']
    bruges_Rp = bruges_zp(vp1, vs1, rho1, vp2, vs2, rho2, theta1=ang)
    test_fig.line(x=ang, y=np.real(bruges_Rp), line_color='black', legend="Bruges_Rp", line_width=2, alpha=0.8)

    test_fig.legend.location = "bottom_right"
    test_fig.legend.click_policy="hide"

    show(test_fig)
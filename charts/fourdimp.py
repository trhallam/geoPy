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
import copy
from data.structLith import structRock
from colorcet import b_diverging_bwr_40_95_c42
from bokeh.models import LinearColorMapper

def chart(bkfig, dryrockmodel, fluidmodel, presmin, presmax):
    '''

    :param bkfig: a bokeh figure pane to populate
    :param rockmodel: a rock model to create the data from
    :return:
    '''
    plot_scale = 100 + 1
    data = np.zeros([plot_scale,plot_scale])

    # setup pressure variations
    dpres = (presmax - presmin)/(plot_scale-1)
    arpres = np.arange(presmin,presmax+dpres,dpres)

    # setup saturation variations
    locfluid = copy.deepcopy(fluidmodel)
    locdrm = copy.deepcopy(dryrockmodel)

    irockmodel = structRock(dryrockmodel,fluidmodel)
    irockmodel.calcGassmann(); irockmodel.calcDensity()
    irockmodel.calcElastic()
    i_imp = irockmodel.pimp

    swi = locfluid.sats[1]
    soi = locfluid.sats[0]
    sgi = locfluid.sats[2]

    dsw = 1.0 / (plot_scale-1)
    arsw = np.arange(0,1+dsw,dsw)
    ratio_og = soi/sgi; total_og = ratio_og+1
    j = 0
    for sw in arsw:
        so = (1-sw)*ratio_og/total_og #saturation oil
        sg = (1-sw)-so #saturation gas
        locfluid.updateSat([so, sw, sg]) #update sats
        i = 0
        for p in arpres:
            locdrm.updatePres(p)
            trock = structRock(locdrm,locfluid)
            trock.calcGassmann(); trock.calcDensity(); trock.calcElastic()
            data[i,j] = 100.*(trock.pimp - i_imp)/i_imp
            i+=1
            #print(sw, so, sg, p, locdrm.Kdry, trock.pimp)
        j+=1

    #plotting stuff
    print(data.min(),data.max())
    dicm = LinearColorMapper(palette=b_diverging_bwr_40_95_c42,low=-5,high=5)
    # must give a vector of image data for image parameter
    bkfig.image(image=[data], x=presmin, y=0, dw=presmax, dh=1, color_mapper=dicm)

#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 10-7-2016

# File Name: avoPy.py

# Synopsis:
# Create a plot with blocky avo outputs.

# Calling:
# 

###############################################################################
'''
from func.funcAVOModels import *
from data.structLith import structLith, structAVOMod
from avoPyConfig import *
from templates.plots import *

import bokeh.layouts as bkl
import bokeh.plotting as bkp
import bokeh.models as bkm
import bokeh.models.widgets as bkw

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
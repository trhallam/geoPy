#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 29-7-2016

# File Name: layout.py

# Synopsis:
# Plot templates

# Calling:
# 

###############################################################################
'''

from bokeh.layouts import gridplot
#from bokeh.plotting import figure, output_file
import bokeh.plotting as bkp
import bokeh.models as bkm
#from bokeh.models import ColumnDataSource, HBox, VBoxForm, VBox
#from bokeh.layouts import widgetbox
import bokeh.models.widgets as bkw
#from bokeh.models.widgets import CheckboxGroup, PreText, Panel, Tabs, DataTable, TableColumn


#toggle boxes
#intfnames=[i.name for i in intfMod]; actNames=[i for i in range(len(intfnames))]
#toggleIntf = CheckboxGroup( labels=intfnames,active=actNames)
#titleIntf = PreText(text='Interfaces')




#p = gridplot([[pAVO,pRPRS],[None,pAIVPVS]])
#q = VBox(titleIntf,toggle)

#source = ColumnDataSource(dict(vp=[2000,2400],vs=[1000,1200]))
#columns = [
#        TableColumn(field="vp", title="Velp"),
#        TableColumn(field="vs", title="Vels"),
#    ]
#data_table = DataTable(source=source, columns=columns, width=400, height=280,editable=True)


#tab1 = Panel(HBox(q,p))
#tab1 = Panel(child=p,title='Plots')
#tab2 = Panel(child=data_table,title='Parameters')

#curdoc().add_root(HBox(q,p))
#tabs = Tabs(tabs = [tab1,tab2])

#x=calcRandNorm(3660,135,0.77,0.05)
#print(x)
#y=calcRandNorm(3660,135,np.random.rand(10),0.05)
#print(y)
#show(tabs)
show(pAVO)
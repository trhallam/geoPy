#!/usr/bin/python
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 29-7-2016

# File Name: plots.py

# Synopsis:
# Plot templates

# Calling:
# 

###############################################################################
'''

#from bokeh.plotting import figure, output_file
import bokeh.plotting as bkp
import bokeh.models as bkm
#from bokeh.models import ColumnDataSource, HBox, VBoxForm, VBox
#from bokeh.layouts import widgetbox
import bokeh.models.widgets as bkw
#from bokeh.models.widgets import CheckboxGroup, PreText, Panel, Tabs, DataTable, TableColumn

### DEFAULT SETTINGS FOR PLOTS
TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave,\
        box_select,poly_select,lasso_select"
        
def plotOpt(bkplot):
    bkplot.grid.grid_line_width = 2
    bkplot.grid.grid_line_color = 'black'
    bkplot.grid.minor_grid_line_color = 'grey'
    bkplot.grid.grid_line_alpha = 0.7
    bkplot.grid[0].ticker.desired_num_ticks=3
    bkplot.grid[0].ticker.num_minor_ticks=5
    bkplot.grid[1].ticker.desired_num_ticks=3
    bkplot.grid[1].ticker.num_minor_ticks=5
        

def plotAVO(tools,model):
    '''
    Creates an AVO Intercept and Gradient Plot from a model.
    '''
    #AVO PLOT TYPES
    bkplot=bkp.figure(tools=tools,
                       title='AVO Intercept vs Gradient',
                       y_range=[-0.5,0.5],x_range=[-0.5,0.5],
                       x_axis_label='Intercept',
                       y_axis_label='Gradient')         
    # iterate over each interface in the model    
    for intf in model:
        source = bkm.ColumnDataSource(data=dict(
                                        A=intf.AVOMod[:,6],
                                        B=intf.AVOMod[:,7]))
        bkplot.circle('A','B',
                    color=intf.colour,
                    legend=intf.name, 
                    source = source, size=5)
        bkplot.legend.location='top_right'
    plotOpt(bkplot)
    
    return bkplot

def plotRPRS(tools,model):
    '''
    Creates an AVO RpRs Plot from a model.
    '''
    bkplot=bkp.figure(tools=tools,
                       title='AVO Rp vs Rs',
                       y_range=[-0.5,0.5],x_range=[-0.5,0.5],
                       x_axis_label='Rp',
                       y_axis_label='Rs')         
    # iterate over each interface in the model    
    for intf in model:
        source = bkm.ColumnDataSource(data=dict(
                                        A=intf.AVOMod[:,6],
                                        Rs=intf.AVOMod[:,8]))
        bkplot.circle('A','Rs',
                    color=intf.colour,
                    legend=intf.name, 
                    source = source, size=5)
        bkplot.legend.location='bottom_right'
    plotOpt(bkplot)
    
    return bkplot

def plotAIVPVS(tools,model):
    '''
    Plots lithological property models.
    '''
    #AI vs VPVS
    pAIVPVS = bkp.figure(
        tools=tools,
        title="AI vs VpVs",
        x_axis_label="Acoustic Impedance",y_axis_label="VpVs")

    for col in model:
        pAIVPVS.circle(col.AIMod,col.VPVSMod,color=col.colour,#fill_color="none",
                 legend=col.name,                
                 size=3)

    pAIVPVS.grid.grid_line_width = 2
    return pAIVPVS
    
def plotLMR(tools,model):
    '''
    Plots lithological property models.
    '''
    #AI vs VPVS
    pLMR = bkp.figure(
        tools=tools,
        title="LR vs MR",
        x_axis_label="LR",y_axis_label="MR")

    for col in model:
        pLMR.circle(col.lmrMod,col.murMod,color=col.colour,#fill_color="none",
                 legend=col.name,                
                 size=3)

    pLMR.grid.grid_line_width = 2
    return pLMR
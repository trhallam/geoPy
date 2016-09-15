# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 18:31:43 2016

@author: tony
"""

"""A histogram plot using Highcharts"""

<<<<<<< HEAD
=======
from itertools import chain

import json

>>>>>>> origin/master
import numpy as np
from scipy import stats

from Orange.data import Table
from Orange.widgets import gui, settings, widget, highcharts

import _highcharts.returns as hcReturns

from PyQt4 import QtGui
import PyQt4.QtCore as QtCore

class Histplot(highcharts.Highchart):
    """
    Histplot extends Highchart and just defines some sane defaults:
    * enables rectangle selection,
    * sets the chart type to 'column' 
    * sets the selection callback. The callback is passed a list (array)
      of indices of selected points for each data series the chart knows
      about.
    """
    def __init__(self, selection_callback, **kwargs):
        super().__init__(enable_zoom=True,
                         enable_select='x',
                         chart_type='column',
                         #chart_margin = [100,100,100,100],
                         chart_legend_enabled = False,
                         chart_credit_enabled = False,
                         selection_callback=selection_callback,
                         **kwargs)
                         
        #add the Highcharts Return Options so charts can be preserved                         
        self.hcAPI = hcReturns.returnOptions()
        self.frame.addToJavaScriptWindowObject('hcAPI',self.hcAPI)
        self.hcAPI._excJSFunc(self.frame)
        
        self.frame.evaluateJavaScript("var x = []; x['a']=2; x['b']='hello';")
        test=self.frame.evaluateJavaScript("hcAPI.json_encode(x);")
        test2=json.loads(test)
        
        print(test)  
        print(test2['a'])
        print(test2['b'])      
        #x=self.frame.evaluateJavaScript("dir(hcAPI);")
        x=self.frame.evaluateJavaScript("dir(hcAPI);")
        self.frame.evaluateJavaScript("returnJS.test2();")
        y=self.frame.evaluateJavaScript("dir(returnJS);")
        print(x)
        print(y)
                         
class OWHistPlot(widget.OWWidget):
    """Histogram plot visualisation using Highcharts"""
    name = 'Histogram'
    description = 'Histogram Visualisation for data.'
    icon = "icons/Histogram.svg"
    
    none="(None)"
    
    inputs = [("Data", Table, "set_data")]
    outputs = [("Selected Data", Table)]
    
    # Selected Counting Index for Histogram
    idx_count = settings.Setting('')
    
    # Selected 
    attr_ind = settings.Setting('')
    
    # Selected Bin Size for sorting counted index
    attr_nbin = settings.Setting(10)
    attr_binsize = settings.Setting(0)
    
    # Selected discrete variable to colour charts by (stacked or adjacent)
    idx_group = settings.Setting('')
    
    # calcuated histogram
    dataHist = Table()
    
    # Plot Options
    opt_stacked = settings.Setting(False)
<<<<<<< HEAD
    opt_dist = settings.Setting('(None)')
=======
>>>>>>> origin/master
    
    graph_name = 'histogram'
    
    def __init__(self):
        super().__init__()
        self.data = None
        self.count = None
        self.countlabels = None
        self.indicies = None
        self.binsize = 0
        self.n_selected = 0
        self.series_rows = []
        self.histData = []
        self.histSeriesNames = []
        self.binDet = 'nbins'
        #Create the UI controls for selecting axes attributes
        #Select the Variable to Plot
        varbox = gui.vBox(self.controlArea, "Variable")
        self.countVarView = gui.comboBox(varbox, self, 'idx_count',
                                label='Attribute',
                                orientation='horizontal',
                                callback=self.on_selection,
                                sendSelectedValue=True)

        #Select the Number of bins in the histogram plot
        binbox = gui.vBox(self.controlArea, "Bin Parameters")
        cWW = 75 #control widget width same for all menus
        sbin = gui.spin(binbox, self, 'attr_nbin', minv=1, maxv=100, 
                        label = "N (1-100)",
                        controlWidth=cWW,
                        callback=self._on_set_nbins)
        #specify the size of the bins manually
        lbin = gui.lineEdit(binbox, self, 'attr_binsize', 
                            label = "Bin Size",
                            orientation = gui.Qt.Horizontal,
                            controlWidth=cWW,
                            callback=self._on_set_binsize)
        sbin.setAlignment(gui.Qt.AlignCenter)
        lbin.setAlignment(gui.Qt.AlignCenter)


        #gui.rubber(sbin.box)
        
        #group selection
        groupbox = gui.vBox(self.controlArea, "Group By")
        self.groupVarView = gui.comboBox(groupbox, self, 'idx_group',
                                  label='',
                                  orientation='horizontal',
                                  callback=self.on_selection,
                                  sendSelectedValue=True)
                                  
        #plot options for columns
        plotbox = gui.vBox(self.controlArea, "Plot Options")
        self.cbStacked = gui.checkBox(plotbox, self, 'opt_stacked',
                                      label='Stack Groups',
<<<<<<< HEAD
                                      callback=self.update)
                                      
        self.distVarView = gui.comboBox(plotbox, self, 'opt_dist',
                                        label='Distribution',
                                        callback=self.update)                                      
=======
                                      callback=self.replot)
>>>>>>> origin/master
        #fill from bottom to widgets
        gui.rubber(self.controlArea)
        
        # Create an instance of Historgam plot. Initial Highcharts configuration
        # can be passed as '_'-delimited keyword arguments. See Highcharts
        # class docstrings and Highcharts API documentation for more info and
        # usage examples.
        self.hist = Histplot(selection_callback=self.on_selection,
                                   xAxis_gridLineWidth=0.1,
                                   yAxis_gridLineWidth=0,
                                   title_text='Histogram',
                                   tooltip_shared=False)
                                   # In development, we can enable debug mode
                                   # and get right-click-inspect and related
                                   # console utils available:
                                   #debug=True)
        # Just render an empty chart so it shows a nice 'No data to display'
        # warning
        self.hist.chart()

        self.mainArea.layout().addWidget(self.hist)

    def set_data(self, data):
        '''
        Initial setup and distribution of data for widget.
        '''
        self.data = data
        
        self.clear() #clear the chart


        #Populate countVarView        
        for var in data.domain if data is not None else []:
            if var.is_primitive():
                self.countVarView.addItem(gui.attributeIconDict[var], var.name)
                
        
                
        #Populate groupVarView
        self.groupVarModel = \
            [self.none] + [var for var in data.domain if var.is_discrete]
        self.groupVarView.addItem(self.none); self.idx_group=self.none
        for var in self.groupVarModel[1:]:
            self.groupVarView.addItem(gui.attributeIconDict[var], var.name)
        if data.domain.has_discrete_class:
            self.groupvar_idx = \
                self.groupVarModel[1:].index(data.domain.class_var) + 1
<<<<<<< HEAD
                
        #Distribution Models
        self.distVarModel = \
            [self.none] + ["Normal"]
        self.distVarView.addItem(self.none)
        for var in self.distVarModel[1:]:
            self.distVarView.addItem(var)
        #self.opt_dist=self.none
=======
>>>>>>> origin/master
        
        if data is None:
            self.hist.clear()
            self.indicies = None
            self.commit()
            return
        
        self._setup()
        self.replot()        
        
    def _setup(self):
        '''
        Need to calculate the histogram distribution.
        '''
        if self.data is None or not self.idx_count:
            # Sanity checks failed; nothing to do
            return

        if self.binDet == 'binsize':
            #calculate histogram based on required binsize
            minVal = np.min(self.data[:,self.idx_count])
            maxVal = np.max(self.data[:,self.idx_count])
            print(type(minVal),type(maxVal),maxVal-minVal,type(self.attr_binsize))
            self.attr_nbin = int((maxVal-minVal)/float(self.attr_binsize))+1

        #calculate the simple histogram
        self.histData = []
        self.histSeriesNames = []
        count,indicies=np.histogram(self.data[:,self.idx_count],
                                          bins=self.attr_nbin)
        
        self.count=count; self.indicies=indicies
                                          
        #correct labels for centre of bin            
        countlabels = np.zeros(len(count))
        for i in range(0,len(count)):
            countlabels[i]=indicies[i]+self.binsize/2  
                                          
        self.histData.append(countlabels); self.histData.append(count)
        self.histSeriesNames.append('Mid Points')        
        self.histSeriesNames.append('Total')        
        
                                          
        if self.idx_group != "(None)":
            y = self.data[:, self.data.domain[self.idx_group]].Y.ravel()
            for yval, yname in enumerate(self.data.domain[self.idx_group].values):
                self.histSeriesNames.append(yname)
                #get the rows for the current selected attribute
                tdata = self.data[(y == yval),self.idx_count]
                #calculate group histogram
                count,indicies=np.histogram(tdata,bins=indicies)
                self.histData.append(count)
            
            
            #sort out colours
            colors = self.data.domain[self.idx_group].colors
            colors = [QtGui.QColor(*c) for c in colors]
            self.colors = [i.name() for i in colors]
                                          
        #correct labels for centre of bin            
        self.countlabels = np.zeros(len(self.count))
        for i in range(0,len(self.count)):
            self.countlabels[i]=self.indicies[i]+self.binsize/2                                          
        #self.dataHist.from_numpy()
            
    
        #calculate size of bins from histrogram outputs        
        if len(self.indicies) >= 2:
            self.attr_binsize=np.around(self.indicies[1]-self.indicies[0],decimals=3)
        else:
            self.attr_binsize=0

    def replot(self):
        
        if self.data is None or not self.idx_count:
            # Sanity checks failed; nothing to do
            return   
            
        #round the binsize    
        rbsize2 = np.around(self.binsize/2,decimals=2)
        # Highcharts widget accepts an options dict. This dict is converted
        # to options Object Highcharts JS uses in its examples. All keys are
        # **exactly the same** as for Highcharts JS.
        options = dict(series=[])

        #Plot by group or not by group        
        if self.idx_group == "(None)":
            print('test1')
            options['series'].append(dict(data=self.count,name=self.idx_count))
        else:
            i=2
            print('test2')
            for var in self.histData[2:]:
                options['series'].append(dict(data=var,
                                              name=self.histSeriesNames[i],
                                              color=self.colors[i-2]))
                i+=1
            
            
        kwargs = dict(
            chart_margin = [100,25,80,50],
            title_text = 'Histogram',
            title_x = 25,
            tooltip_crosshairs = True,
            #tooltip_valueDecimals=2,
            plotOptions_series_minPointLength = 2,
            plotOptions_series_pointPadding = 0,
            plotOptions_series_groupPadding = 0,
            plotOptions_series_borderWidth = 1,
            plotOptions_series_borderColor = 'rgba(255,255,255,0.5)',
            xAxis_labels_format = '{value:.2f}',
            #xAxis_title_text = 'Test',
            #xAxis_linkedTo = 0,
            xAxis_gridLineWidth = 0.5,
            xAxis_gridLineColor = 'rgba(0,0,0,0.25)',
            xAxis_gridZIndex = 8,
            yAxis_maxPadding = 0,
            yAxis_gridLineWidth = 0.5,
            yAxis_gridLineColor = 'rgba(0,0,0,0.25)',
            yAxis_gridZIndex = 0,
            yAxis_title_text = 'Frequency')
        
        if self.opt_stacked:
            kwargs['plotOptions_column_stacking']='normal'
        
        #if self.indicies.is_discrete:
<<<<<<< HEAD
        if self.data.domain[self.idx_count].is_discrete:
            kwargs['xAxis_categories']=self.countlabels
        else:
            kwargs['xAxis_categories']=np.around(self.countlabels,decimals=2)
            kwargs['xAxis_labels_format'] = '{value:.2f}'
            
        #test distribution
        #if self.opt_dist == "Normal":
        if self.distVarView.currentText() != "(None)":
            #Normal Distribution            
            if self.distVarView.currentText() == "Normal":
                #fit the data
                mu, std = stats.norm.fit(self.data[:,self.idx_count])
                #calculate the x values
                x = np.linspace(self.countlabels[0],self.countlabels[-1],100)
                #calculate x values that match the histogram column space
                xcol = np.linspace(0,self.attr_nbin,100)
                #calculate the normal distribution curve
                distr = stats.norm.pdf(x, mu, std)
                surv = stats.norm.sf(x, mu, std)
                #add to the chart
                options['series'].append(dict(data=np.column_stack([xcol,distr]),
                                              name='Normal Distribution',
                                              #marker = {enabled : False},
                                              lineWidth = 3,
                                              #xAxis = 1,
                                              yAxis = 1,
                                              showInLegend=False))#,
                                              
                #Chart Type cannot be added via options due to special type name
                options['series'][-1]['type']='scatter'
                options['series'][-1]['id']='normal'
                options['series'][-1]['marker']=dict(radius=1)
                options['series'][-1]['marker']=dict(radius=1)
                
                #add survival series
                options['series'].append(dict(data=np.column_stack([xcol,surv]),
                                              name='surv',
                                              visible=False,
                                              showInLegend=False))
                options['series'][-1]['type']='scatter'
                options['series'][-1]['id']='surv'
                
        options['tooltip']={
            #'valueDecimals':'3',
            'shared' : True,
            'formatter': '''/**/(function() {
                var text = '';
                if(this.series.name == 'Normal Distribution') {
                    text = this.x + ' ' + this.y + ' ';                
                } else {
                    text = ('<b>' + this.y +
                        '</b> points <br> in bin: <b>' +
                       (this.x - %.2f) + '</b>-<b>' +
                       (this.x + %.2f) + '</b>');
                }
                return text; })'''%(rbsize2,rbsize2)}

=======
        kwargs['xAxis_categories']=np.around(self.countlabels,decimals=2)
        
>>>>>>> origin/master
#        self.hist.chart(options,javascript=self.hello(), **kwargs)           
        #self.hist.chart(options,javascript_after="pybridge['hello']='world'", **kwargs)           
        self.hist.chart(options, **kwargs)
        print(self.hist.frame.evaluateJavaScript("dir(chart);"))
       # print(self.hist.frame.evaluateJavaScript("chart.series;"))
        print(self.hist.frame.evaluateJavaScript("returnJS.getLegendSelectedSeries(chart);"))
        
#    def getHCStatus(self):
#        '''
#        Find out whether series are turned on or off.
#        '''
#        self.hist.evalJS()

    def _on_set_nbins(self):
        self.binDet = 'nbins'
        self._setup()
        self.replot()
        
    def _on_set_binsize(self):
        self.binDet = 'binsize'
        self._setup()
        self.replot()
        return
        
    def on_selection(self):
        self._setup()
        self.replot()
        
    def commit(self):
        self.send('Selected Data',
                  self.data[self.indicies] if self.indicies else None)
                  
    def send_report(self):
        self.report_data('Data', self.data)
        self.report_raw('Histogram', self.scatter.svg())
        
    def update(self):   
        #self.idx_group = self.groupVarView.currentText()
        #self.opt_dist = self.distVarView.currentText()
        self.replot()
        
    def clear(self):
        '''
        Clear all data from the chart and reimport data.
        '''
        self.hist.clear()
        #clear chart with reset
        self.countVarView.clear()
        self.groupVarView.clear()

        #reset import attributes
        self.attr_nbin = 10
        self.attr_binsize = 0
        

def main():
    from PyQt4.QtGui import QApplication
    app = QApplication([])
#    print(dir(app))
    ow = OWHistPlot()
#    print(dir(ow))
    data = Table("iris")
    ow.set_data(data)
    ow.show()
    app.exec_()


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 18:31:43 2016

@author: tony
"""

"""A histogram plot using Highcharts"""

from itertools import chain

import numpy as np
from scipy import stats

from Orange.data import Table
from Orange.widgets import gui, settings, widget, highcharts

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
                         chart_margin = [100,100,100,100],
                         chart_legend_enabled = False,
                         chart_credit_enabled = False,
                         selection_callback=selection_callback,
                         **kwargs)
                         
class OWHistPlot(widget.OWWidget):
    """Histogram plot visualisation using Highcharts"""
    name = 'Histogram'
    description = 'Histogram Visualisation for data.'
    icon = "icons/Histogram.svg"
    
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
        
        groupbox = gui.vBox(self.controlArea, "Group By")
        self.groupVarView = gui.comboBox(groupbox, self, 'idx_group',
                                  label='',
                                  orientation='horizontal',
                                  callback=self.on_selection,
                                  sendSelectedValue=True)        
        
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
            ["(None)"] + [var for var in data.domain if var.is_discrete]
        self.groupVarView.addItem("(None)")
        for var in self.groupVarModel[1:]:
            self.groupVarView.addItem(gui.attributeIconDict[var], var.name)
        if data.domain.has_discrete_class:
            self.groupvar_idx = \
                self.groupVarModel[1:].index(data.domain.class_var) + 1
        
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
        self.count,self.indicies=np.histogram(self.data[:,self.idx_count],
                                          bins=self.attr_nbin)
    
        #calculate size of bins from histrogram outputs        
        if len(self.indicies) >= 2:
            self.attr_binsize=np.around(self.indicies[1]-self.indicies[0],decimals=3)
        else:
            self.attr_binsize=0


        #correct labels for centre of bin            
        self.countlabels = np.zeros(len(self.count))
        for i in range(0,len(self.count)):
            self.countlabels[i]=self.indicies[i]+self.binsize/2
            

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
        options['series'].append(dict(data=self.count,name=self.idx_count))
        kwargs = dict(
            chart_margin = [100,25,50,50],
            title_text = 'Histogram',
            title_x = 25,
            tooltip_crosshairs = True,
            tooltip_formatter = '''/**/(function() {
                                return ('<b>' + this.y +
                                '</b> points <br> in bin: <b>' +
                                (this.x - %.2f) + '</b>-<b>' +
                                (this.x + %.2f) + '</b>');})
                                '''%(rbsize2,rbsize2),
            plotOptions_series_minPointLength = 2,
            plotOptions_series_pointPadding = 0,
            plotOptions_series_groupPadding = 0,
            plotOptions_series_borderWidth = 0.5,
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
        
        #if self.indicies.is_discrete:
        kwargs['xAxis_categories']=np.around(self.countlabels,decimals=2)
        
#        self.hist.chart(options,javascript=self.hello(), **kwargs)           
#        self.hist.chart(options,javascript_after=self.hello(), **kwargs)           
        self.hist.chart(options, **kwargs)           

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
    ow = OWHistPlot()
    data = Table("iris")
    ow.set_data(data)
    ow.show()
    app.exec_()


if __name__ == "__main__":
    main()
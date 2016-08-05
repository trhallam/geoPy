# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 18:31:43 2016

@author: tony
"""

"""A histogram plot using Highcharts"""

from itertools import chain

import numpy as np
from scipy import stats

from PyQt4.QtCore import Qt

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
                         chart_margin = [100,25,50,50],
                         selection_callback=selection_callback,
                         **kwargs)

class OWHistPlot(widget.OWWidget):
    """Histogram plot visualisation using Highcharts"""
    name = 'Histogram'
    description = 'Histogram Visualisation for data.'
    icon = "icons/Histogram.svg"
    
    inputs = [("Data", Table, "set_data")]
    outputs = [("Selected Data", Table)]
    
    attr_count = settings.Setting('')
    attr_ind = settings.Setting('')
    attr_bins = settings.Setting(10)
    
    graph_name = 'histogram'
    
    def __init__(self):
        super().__init__()
        self.data = None
        self.count = None
        self.indicies = None
        self.n_selected = 0
        self.series_rows = []
        #Create the UI controls for selecting axes attributes
        #Select the Variable to Plot
        varbox = gui.vBox(self.controlArea, "Variable")
        self.var = gui.comboBox(varbox, self, 'attr_count',
                                label='Attribute',
                                orientation='horizontal',
                                callback=self.on_selection,
                                sendSelectedValue=True)
        #Select the Number of bins in the histogram plot
        binbox = gui.vBox(self.controlArea, "Number of Bins")
        sbin = gui.spin(binbox, self, 'attr_bins', minv=1, maxv=100, 
                        label = "N (1-100) = ",
                        callback=self._on_set_nbins)
        #sbin.setMaximumWidth=200
        sbin.setAlignment(Qt.AlignCenter)
        #gui.rubber(sbin.box)
        
        #fill from bottom to widgets
        gui.rubber(self.controlArea)
        
        # Create an instance of Historgam plot. Initial Highcharts configuration
        # can be passed as '_'-delimited keyword arguments. See Highcharts
        # class docstrings and Highcharts API documentation for more info and
        # usage examples.
        self.hist = Histplot(selection_callback=self.on_selection,
                                   xAxis_gridLineWidth=0,
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
        self.data = data
        
        #clear chart with reset
        self.var.clear()
        for var in data.domain if data is not None else []:
            if var.is_primitive():
                self.var.addItem(gui.attributeIconDict[var], var.name)
        
        if data is None:
            self.hist.clear()
            self.indicies = None
            self.commit()
            return
        
        self._setup()        
        
    def _setup(self):
        '''
        Need to calculate the histogram distribution.
        '''
        if self.data is None or not self.attr_count:
            # Sanity checks failed; nothing to do
            return

        #calculate the simple histogram
        self.count,self.indicies=np.histogram(self.data[:,self.attr_count],
                                              bins=self.attr_bins)

    def replot(self):
    
        if self.data is None or not self.attr_count:
            # Sanity checks failed; nothing to do
            return   
        #print('Replotting')    
        # Highcharts widget accepts an options dict. This dict is converted
        # to options Object Highcharts JS uses in its examples. All keys are
        # **exactly the same** as for Highcharts JS.
        options = dict(series=[])
        options['series'].append(dict(data=self.count))
        #print(options)
        kwargs = dict(
            chart_margin = [100,25,50,50],
            title_text = 'Histogram',
            title_x = 25,
#            legend_enabled = False,
#            credits_enables = False,
#            exporting_enabled = False,
            tooltip_crosshairs = True,
            plotOptions_series_minPointLength = 2,
            plotOptions_series_pointPadding = 0,
            plotOptions_series_groupPadding = 0,
            plotOptions_series_borderWidth = 0.5,
            plotOptions_series_borderColor = 'rgba(255,255,255,0.5)',
            xAxis_title_text = 'Test',
            yAxis_title_text = 'Frequency')
            
        self.hist.chart(options, **kwargs)           

    def _on_set_nbins(self):
        self._setup()
        self.replot()
        
    def on_selection(self):
        self._setup()
        self.replot()
        
    def commit(self):
        self.send('Selected Data',
                  self.data[self.indicies] if self.indicies else None)
                  
    def send_report(self):
        self.report_data('Data', self.data)
        self.report_raw('Histogram', self.scatter.svg())                  
        
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
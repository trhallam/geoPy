# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 18:31:43 2016

@author: tony
"""

"""A histogram plot using Highcharts"""

from itertools import chain

import json
import os

import numpy as np
from scipy import stats

from Orange.data import Table
from Orange.widgets import gui, settings, widget, highcharts

from PyQt4 import QtGui, QtCore

class returnJS(QtCore.QObject):
    '''
    Return the Options from Highcharts Chart
    '''

    def __init__(self, parent=None):
        super(returnJS, self).__init__(parent)
        __location__ = os.path.dirname(__file__) 


        #Special JS Functions to load for interaction.
        jScripts = ['returns',
                    'dir']
        self.jsFunc=['returnJS={};']
        for script in jScripts:
            scriptPath = os.path.join(__location__,script)+'.js'
            #print(os.path.realpath(scriptPath))
            with open(os.path.realpath(scriptPath),'r') as myfile:
                self.jsFunc.append(myfile.read().replace('\n','')+';')
        
        self.jsFunc.append("returnJS.hello = function() {alert('Hello World!');}")
        self.jsFunc.append("returnJS.test = {}; returnJS.test['a'] = 1;\
                                          returnJS.test['b'] = 'Hello';")
        #print("Python:",self.jsFunc)
        
    # take a javascript object and return string
    # javascript objects come into python as dictionaries
    # functions are represented by an empty dictionary
    @QtCore.pyqtSlot('QVariantMap', result=str)
    def json_encode(self, jsobj):
        # import is here to keep it separate from 'required' import
        return json.dumps(jsobj)
        
    # dump messages from JS to Python Console for debugging
    @QtCore.pyqtSlot(str)
    def consoleDump(self, message):
        print('JS: '+ message)
        
        # dump messages from JS to Python Console for debugging
    @QtCore.pyqtSlot(str, result=str)
    def passStr(self, jsstr):
        return jsstr
    
    # take a list of strings and return a string
    # because of setapi line above, we get a list of python strings as input
    @QtCore.pyqtSlot('QStringList', result=str)
    def concat(self, strlist):
        return ''.join(strlist)
    
class HighchartExt(highcharts.Highchart):
    """
    Histplot extends Highchart and just defines some sane defaults:
    * enables rectangle selection,
    * sets the chart type to 'column' 
    * sets the selection callback. The callback is passed a list (array)
      of indices of selected points for each data series the chart knows
      about.
    """
    def __init__(self, **kwargs):
        super().__init__(enable_zoom=True,
                         #enable_select='xy+',
                         chart_type='scatter',
                         #selection_callback=selection_callback,
                         **kwargs)
                         
        self.returnJS=returnJS()
        #self.frame.javaScriptWindowObjectCleared.connect(self.loadAPI)
        #self.frame.javaScriptWindowObjectCleared.connect(self.getLegendSelectedSeries)
        #self.loadAPI()
        
    # event handler for javascript window object being cleared        
    #def loadAPI(self):
        self.frame.addToJavaScriptWindowObject('returnAPI',self.returnJS)
        # add external functions to returnJS
        for scr in self.returnJS.jsFunc:
            #print(scr)
            self.evalJS(scr)

#        self.evalJS("returnJS.hello();")
        #self.evalJS("returnJS.testR = returnJS.dir(returnJS);")    
#        self.evalJS("alert('returnjs'+returnJS.testR);")
       # self.evalJS("returnAPI.consoleDump('Hello Console Dump!');")
        #self.evalJS("returnAPI.consoleDump(returnJS.testR);")

    def getLegendSelectedSeries(self):
        self.evalJS('visibleSeries = returnJS.getLegendSelectedSeries(window.chart);')
        self.evalJS('returnAPI.consoleDump(returnAPI.json_encode(visibleSeries));')  
        self.evalJS("returnAPI.consoleDump('dir:'+returnJS.dir(visibleSeries));") 
        self.evalJS("returnAPI.consoleDump('acc:'+visibleSeries['Iris-versicolor']);") 
        VS = self.evalJS('returnAPI.json_encode(visibleSeries);')
        self.evalJS('VS = returnAPI.json_encode(visibleSeries);')
        self.visibleSeries = self.evalJS('returnAPI.passStr(VS);')

        if self.visibleSeries != None:
            print('json')
            self.visibleSeries=json.loads(self.visibleSeries)
        
        
def main():
    class OWScatterPlot(widget.OWWidget):
        """Example scatter plot visualization using Highcharts"""
        name = 'Simple Scatter Plot'
        description = 'An example scatter plot visualization using Highcharts.'
        icon = "icons/ScatterPlot.svg"
    
        inputs = [("Data", Table, "set_data")]
        outputs = [("Selected Data", Table)]
    
        attr_x = settings.Setting('')
        attr_y = settings.Setting('')
    
        graph_name = 'scatter'
    
        def __init__(self):
            super().__init__()
            self.data = None
            self.indices = None
            self.n_selected = 0
            self.series_rows = []
            # Create the UI controls for selecting axes attributes
            box = gui.vBox(self.controlArea, 'Axes')
            self.cbx = gui.comboBox(box, self, 'attr_x',
                                    label='X:',
                                    orientation='horizontal',
                                    callback=self.replot,
                                    sendSelectedValue=True)
            self.cby = gui.comboBox(box, self, 'attr_y',
                                    label='Y:',
                                    orientation='horizontal',
                                    callback=self.replot,
                                    sendSelectedValue=True)
            gui.label(self.controlArea, self, '%(n_selected)d points are selected',
                      box='Info')
            gui.rubber(self.controlArea)
    
            # Create an instance of Scatter plot. Initial Highcharts configuration
            # can be passed as '_'-delimited keyword arguments. See Highcharts
            # class docstrings and Highcharts API documentation for more info and
            # usage examples.
            self.scatter = HighchartExt(selection_callback=self.on_selection,
                                       xAxis_gridLineWidth=0,
                                       yAxis_gridLineWidth=0,
                                       title_text='Scatterplot example',
                                       tooltip_shared=False,
                                       # In development, we can enable debug mode
                                       # and get right-click-inspect and related
                                       # console utils available:
                                       debug=True)
            # Just render an empty chart so it shows a nice 'No data to display'
            # warning
            self.scatter.chart()
    
            self.mainArea.layout().addWidget(self.scatter)
    
        def set_data(self, data):
            self.data = data
    
            # When the widget receives new data, we need to:
    
            # ... reset the combo boxes ...
    
            def init_combos():
                self.cbx.clear()
                self.cby.clear()
                for var in data.domain if data is not None else []:
                    if var.is_primitive():
                        self.cbx.addItem(gui.attributeIconDict[var], var.name)
                        self.cby.addItem(gui.attributeIconDict[var], var.name)
    
            init_combos()
    
            # If the data is actually None, we should just
            # ... reset the scatter plot, selected indices ...
            if data is None:
                self.scatter.clear()
                self.indices = None
                self.commit()
                return
    
            # ... else, select the first two attributes and replot the scatter.
            if len(data.domain) >= 2:
                self.attr_x = self.cbx.itemText(0)
                self.attr_y = self.cbx.itemText(1)
            self.replot()
    
        def replot(self):
            # Brace yourself ...
    
            if self.data is None or not self.attr_x or not self.attr_y:
                # Sanity checks failed; nothing to do
                return
    
            data = self.data
            attr_x, attr_y = data.domain[self.attr_x], data.domain[self.attr_y]
    
            # Highcharts widget accepts an options dict. This dict is converted
            # to options Object Highcharts JS uses in its examples. All keys are
            # **exactly the same** as for Highcharts JS.
            options = dict(series=[])
    
            # For our scatter plot, we need data in a standard numpy 2D array,
            # with x and y values in the two columns ...
            cols = []
            for attr in (attr_x, attr_y):
                subset = data[:, attr]
                cols.append(subset.Y if subset.Y.size else subset.X)
            # ... that's our X here
            X = np.column_stack(cols)
    
            # Highcharts point selection returns indexes of selected points per
            # each input series. Thus we should maintain a "map" of such indices
            # into the original data table.
            self.series_rows = []
    
            # If data has a discrete class, we want to color nodes by it, and we
            # do so by constructing a separate instance series for each class
            # value. This is one way of doing it. If you know of a better one,
            # you must be so lucky and I envy you!!
            if data.domain.has_discrete_class:
                y = data[:, data.domain.class_var].Y.ravel()
                for yval, yname in enumerate(data.domain.class_var.values):
                    rows = (y == yval).nonzero()[0]
                    self.series_rows.append(rows)
                    options['series'].append(dict(data=X[rows], name=yname))
            # If data doesn't have a discrete class, just use the whole data as
            # a single series (colored with default color — no gradient fill in
            # this example).
            else:
                self.series_rows.append(np.arange(len(X)))
                options['series'].append(dict(data=X, showInLegend=False))
    
            # Besides the options dict, Highcharts can also be passed keyword
            # parameters, where each parameter is split on underscores in
            # simulated object hierarchy. This works:
            kwargs = dict(
                xAxis_title_text=attr_x.name,
                yAxis_title_text=attr_y.name,
                tooltip_headerFormat=(
                    '<span style="color:{point.color}">\u25CF</span> '
                    '{series.name} <br/>'),
                tooltip_pointFormat=(
                    '<b>{attr_x.name}:</b> {{point.x}}<br/>'
                    '<b>{attr_y.name}:</b> {{point.y}}<br/>').format_map(locals()))
            # If any of selected attributes is discrete, we correctly scatter it
            # as a categorical
            if attr_x.is_discrete:
                kwargs['xAxis_categories'] = attr_x.values
            if attr_y.is_discrete:
                kwargs['yAxis_categories'] = attr_y.values
    
            # That's it, we can scatter our scatter by calling its chart method
            # with the parameters we'd constructed
            self.scatter.chart(options, **kwargs)
            
            self.scatter.getLegendSelectedSeries()
    
        def on_selection(self, indices):
            # When points on the scatter plot are selected, this method is called.
            # Variable indices contains indices of selected points **per each
            # input series** (series in the options object above).
            # Luckily, we kept original data indices that form each of the
            # series ...
            self.indices = list(chain.from_iterable(
                self.series_rows[i][selected]
                for i, selected in enumerate(indices)
            ))
    
            # Let's give the user some feedback
            self.n_selected = len(self.indices)
    
            # And that's it, we can commit the output!
            self.commit()
    
        def commit(self):
            self.send('Selected Data',
                      self.data[self.indices] if self.indices else None)
    
        def send_report(self):
            self.report_data('Data', self.data)
            self.report_raw('Scatter plot', self.scatter.svg())


    from PyQt4.QtGui import QApplication
    app = QApplication([])
    ow = OWScatterPlot()
    data = Table("iris")
    ow.set_data(data)
    #ow.scatter.evalJS('visibleSeries = returnJS.getLegendSelectedSeries(window.chart);')
    #ow.scatter.evalJS('returnJS.visibleSeries = returnJS.test;')
    #selectedSeries = ow.scatter.evalJS("returnAPI.json_encode(returnJS.test);")
    #ow.scatter.evalJS("returnAPI.consoleDump(returnJS.test['a']);")
    #ow.scatter.evalJS("returnJS.testR = returnJS.dir(window.chart.series);")    
    ow.scatter.frame.evaluateJavaScript("returnAPI.consoleDump('Hello Console Dump!');")
    #ow.scatter.evalJS("returnAPI.consoleDump(window.chart.series[0].name);")
    #ow.scatter.evalJS("returnAPI.consoleDump(returnJS.test['a']);")
    #print('json_encode: '+ selectedSeries)
    #print(json.loads(selectedSeries))
        
    ow.show()    

    app.exec_()


if __name__ == "__main__":
    main()



#if __name__ == '__main__':
#    import sys
#    from PyQt4.QtGui import QApplication
#    from PyQt4.QtWebKit import QWebView
#
#    app = QApplication(sys.argv)
#
#    view = HighchartExt()
#
##Test adding function    
#    view.api.jsFunc="/**/(function hello() {alert('Hello World!');})"
#    print(view.api.jsFunc)
#    view.frame.evaluateJavaScript(view.api.jsFunc)
##    view.api._excJSFunc(view.frame)
##    view.frame.evaluateJavaScript(view.api.jsFunc)
#    
#    view.frame.evaluateJavaScript("hello();")   
#    view.frame.evaluateJavaScript("alert('alert');")       
#    
##    view.frame.evaluateJavaScript("var x = []; x['a']=2; x['b']='hello';")
##    view.frame.evaluateJavaScript("var y = {}; y.a = 1; y.b = 'helloy';")
##    view.frame.evaluateJavaScript("alert(x['a']);")    
##    test=view.frame.evaluateJavaScript("pyapi.json_encode(x);")
##    test2=json.loads(test)
##    test3=view.frame.evaluateJavaScript("pyapi.json_decode(x);")
##    view.api._excJSFunc(view.frame)    
##    view.frame.evaluateJavaScript("hello();")
##    view.frame.evaluateJavaScript("var test = dir(y); pyapi.consoleDump(test);")    
##    test4=view.frame.evaluateJavaScript("var test = dir(y); pyapi.concat(test);")
##    print(test)
##    print(test3)
##    print(test2['a'])
##    print(test2['b'])
##    print(test4)
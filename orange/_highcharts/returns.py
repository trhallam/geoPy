"""
This module contains the class and functions necessary to return options from 
highcharts so that they can be preserved for when charts are updated or 
reopened.
"""


import PyQt4.QtCore as QtCore
import json
import os

class returnOptions(QtCore.QObject):
    '''
    Return the Options from Highcharts Chart
    '''

    def __init__(self, parent=None):
        super(returnOptions, self).__init__(parent)
        __location__ = os.path.dirname(__file__) 


        #Special JS Functions to load for interaction.
        jScripts = ['returns',
                    'dir']
        self.jsFunc=''
        for script in jScripts:
            scriptPath = os.path.join(__location__,script)+'.js'
            #print(os.path.realpath(scriptPath))
            with open(os.path.realpath(scriptPath),'r') as myfile:
                self.jsFunc += myfile.read().replace('\n','')
            self.jsFunc+=';'
                
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
        print( message)
    
    # take a list of strings and return a string
    # because of setapi line above, we get a list of python strings as input
    @QtCore.pyqtSlot('QStringList', result=str)
    def concat(self, strlist):
        return ''.join(strlist)
    
    #Java string of code to find out which series are visible.    
    def _excJSFunc(self,frame):
        frame.evaluateJavaScript(self.jsFunc)
        
        
html = """
<html>
<body>
    <h1>Hello!</h1><br>
    <h2><a href="#" onclick="printer.text('Message from QWebView')">QObject Test</a></h2>
    <h2><a href="#" onclick="alert('Javascript works!')">JS test</a></h2>
</body>
</html>
"""

if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication
    from PyQt4.QtWebKit import QWebView

    # client webview which will have QObject js->python bridge
    class Client(QWebView):
        def __init__(self):
            super(Client, self).__init__()
    
            # create python api object
            self.api = returnOptions()
    
            # get the main frame of the view so that we can load the api each time
            # the window object is cleared
            self.frame = self.page().mainFrame()
            self.frame.javaScriptWindowObjectCleared.connect(self.load_api)
    
        # event handler for javascript window object being cleared
        def load_api(self):
            # add pyapi to javascript window object
            # slots can be accessed in either of the following ways -
            #   1.  var obj = window.pyapi.json_decode(json);
            #   2.  var obj = pyapi.json_decode(json)
            self.frame.addToJavaScriptWindowObject('pyapi', self.api)

    app = QApplication(sys.argv)

    view = Client()

#Test adding function    
    view.api.jsFunc="/**/(function hello() {alert('Hello World!');})"
    print(view.api.jsFunc)
    view.frame.evaluateJavaScript(view.api.jsFunc)
#    view.api._excJSFunc(view.frame)
#    view.frame.evaluateJavaScript(view.api.jsFunc)
    
    view.frame.evaluateJavaScript("hello();")   
    view.frame.evaluateJavaScript("alert('alert');")       
    
#    view.frame.evaluateJavaScript("var x = []; x['a']=2; x['b']='hello';")
#    view.frame.evaluateJavaScript("var y = {}; y.a = 1; y.b = 'helloy';")
#    view.frame.evaluateJavaScript("alert(x['a']);")    
#    test=view.frame.evaluateJavaScript("pyapi.json_encode(x);")
#    test2=json.loads(test)
#    test3=view.frame.evaluateJavaScript("pyapi.json_decode(x);")
#    view.api._excJSFunc(view.frame)    
#    view.frame.evaluateJavaScript("hello();")
#    view.frame.evaluateJavaScript("var test = dir(y); pyapi.consoleDump(test);")    
#    test4=view.frame.evaluateJavaScript("var test = dir(y); pyapi.concat(test);")
#    print(test)
#    print(test3)
#    print(test2['a'])
#    print(test2['b'])
#    print(test4)
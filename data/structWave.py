###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 30-7-2016

# File Name: structWave.py

# Synopsis:
# Basic class and functions for Wavelets.
# Currently used for avo modelling, wedge modelling, wavelet Demo.

###############################################################################

from func.funcWave import *
from func.funcFilter import *
import numpy as np
import copy

class structWave(object):
    """ 
    This class is used to represent and deal with wavelets in time.
    """
    
    def __init__(self,name,colour,ns,dt):
        "Initiate lithology properties."
        self.name=name
        self.colour=colour
        self.dt=dt
        self.sr=1/self.dt
        self.ns=ns                          #Number of Samples
        self.nyquist=(self.dt**-1.0)*1000/2.0 #Nyquist frequency of samples
        self.df=self.nyquist/((self.ns-1)/2.0)
        self.timeseries=np.zeros(ns)        #Blank array for time series
        self.timeAmp=np.zeros(ns)
        self.freqseries=np.zeros(ns)
        self.ampSpec=np.zeros(ns)           #Blank array for amp spectrum
        self.powSpec=np.zeros(ns)           #Blank array for power spectrum
        self.phase=np.zeros(ns)             #Blank array for phase by freq
        

    def typeRicker(self,domFreq):
        self.timeseries=makeMirrorTime(self.ns,self.dt)
        self.timeAmp=ricker(len(self.timeseries),self.dt,domFreq)
        
    def typeBandPass(self,lowCut,lowPass,highPass,highCut):
        '''
        Create a bandpass wavelet.
        '''
        self.timeseries=makeMirrorTime(self.ns,self.dt)
        self.freqseries,self.ampSpec=makeBandPass(self.nyquist,self.df,
                                  lowCut,lowPass,highPass,highCut)
        self.orgSpec=self.ampSpec.copy()
        self.timeAmp=transAmpSpec(self.ampSpec,self.df,t='backwards')
        self.timeAmp=self.timeAmp/np.amax(self.timeAmp)
                
    def typeOrmsby(self,f1,f2,f3,f4):
        '''
        Create an Ormsby Wavelet
        '''
        self.timeseries=makeMirrorTime(self.ns,self.dt)
        def oC(fa,fb,fc):
            return (np.pi*fa)*(np.pi*fa)/(np.pi*(fb-fc))
        def sC(ft):
            return np.sinc(np.pi*ft)*np.sinc(np.pi*ft)
        self.timeAmp = (oC(f4,f4,f3)*sC(f4*self.timeseries/1000.)- \
                       oC(f3,f4,f3)*sC(f3*self.timeseries/1000.))- \
                       (oC(f2,f2,f1)*sC(f2*self.timeseries/1000.)+ \
                       oC(f1,f2,f1)*sC(f1*self.timeseries/1000.))  
        self.timeAmp=self.timeAmp/np.amax(self.timeAmp)          
        
    def calcAmpSpec(self):
        self.ampSpec,self.freqseries=transAmpSpec(self.timeAmp,self.dt)        
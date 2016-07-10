###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 10-7-2016

# File Name: structLith.py

# Synopsis:
# Basic class and functions for blocky lithology.
# Currently used for avo modelling.

###############################################################################

from func.funcAVOModels import calcRandNorm, calcAVO
import numpy as np
import copy

class structLith(object):
    """ 
    This class is used to represent and deal with tops/interval logs.
    """
    
    def __init__(self,name,colour,Vp,Vs,Rho,VpStd,VsStd,RhoStd):
        "Initiate lithology properties."
        self.name=name
        self.colour=colour
        self.Vp=Vp      #P-wave velocity
        self.Vs=Vs      #S-wave velocity
        self.Rho=Rho    #Density
        self.AI=Vp*Rho  #Acoustic Impedance
        self.SI=Vs*Rho  #Shear Impedance
        self.VPVS=Vp/Vs #VpVs Ratio
        
        self.VpStd=VpStd        
        self.VsStd=VsStd
        self.RhoStd=RhoStd
        
    def calcModel(self,nsims,var):
        self.nsims=nsims
        self.var=var
        
        self.seed=np.random.rand(nsims)
        self.VpMod=calcRandNorm(self.Vp,self.VpStd,self.seed,var)
        self.VsMod=calcRandNorm(self.Vs,self.VsStd,self.seed,var)
        self.RhoMod=calcRandNorm(self.Rho,self.RhoStd,self.seed,var)
        self.AIMod=self.VpMod*self.RhoMod
        self.SIMod=self.VsMod*self.RhoMod
        self.VPVSMod=self.VpMod/self.VsMod
        
class structAVOMod(object):
    
    def __init__(self,lith1,lith2,nsims,var,colour):
        self.topName=lith1.name
        self.botName=lith2.name
        self.name = self.topName+" on "+self.botName
        self.colour=colour
        self.topMod=copy.deepcopy(lith1)
        self.botMod=copy.deepcopy(lith2)
        
        self.topMod.calcModel(nsims,var)
        self.botMod.calcModel(nsims,var)
        
        self.AVOMod = calcAVO(self.topMod.VpMod,self.botMod.VpMod,
                              self.topMod.VsMod,self.botMod.VsMod,
                              self.topMod.RhoMod,self.botMod.RhoMod)
        
        
        #others to follow as required        
        


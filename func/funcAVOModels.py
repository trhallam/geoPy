###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 9-7-2016

# File Name: funcAVOModels.py

# Synopsis:
# Basic functions related to AVO Modelling.

###############################################################################

import numpy as np
import scipy.stats as sps

def calcRandNorm(mean,std,seed,var):
    """
    Calculates a random value from the mean & standard deviation for a normal
    distribution. Seed is used to set the point on the lognormal curve 0-100% 
    and var is the % variation allowed around that point.
    
    input:
            mean : mean value or centre of lognormal distribution
            std  : standard deviation of distribution
            seed : seed point on random distribution (generally a random number)
            var  : variation allowed around seed point in %

    output:
            new semi random value which meets input criteria
"""

    varR = (seed*(1.0+var)-seed*(1.0-var))
    val   = np.random.random(size=np.size(varR))*varR+seed
    np.clip(val,0.01,0.99,out=val)
    val = sps.norm.ppf(val,loc=mean,scale=std)
    return val
    
def modelAVOAkiRichards3(interface):
    """
    Calculates the AVO parameters using Aki-Richards 3-term approximation.
    
    Intercept A and Rp
    A=0.5 * ((dVp/Vp)+(drho/rho))
    Gradient B
    
    
    """
    interface[:,6]=0.5*(interface[:,0]/interface[:,3]+ \
                        interface[:,2]/interface[:,5])
    interface[:,7]=(interface[:,0]/(2*interface[:,3]))- \
                        4*((interface[:,4]**2/interface[:,3]**2)* \
                        (interface[:,1]/interface[:,4]))- \
                        2*(interface[:,4]**2/interface[:,3]**2)* \
                        (interface[:,2]/interface[:,5])
                        
def modelFattiRpRs(interface,vpvs=0.5):
    """
    Calculates the Rs Term for the fatti equation.
    """
    interface[:,8]=vpvs*(interface[:,6]-interface[:,7])

def calcAVO(velp1,velp2,vels1,vels2,rho1,rho2,model='akirichards3'):
    """
    Calculates the avo parameters related to a blocky interface.
    
    input:
            velp1 : Top halfspace P-wave Velocity
            velp2 : Bottom halfspace P-wave Velocity
            vels1 : Top halfspace S-wave Velocity
            vels2 : Bottom halfspace S-wave Velocity
            rho1  : Top halfspace Density
            rho2  : Bottom halfspace Density
            
    output:
            array of accoustic properties
            dVp,dVs,dRho,Vp,Vs,Rho,A,B,Rp,Rs

    
    """
    out=np.zeros([np.size(velp1),9])
    out[:,0]=velp2-velp1
    out[:,1]=vels2-vels1
    out[:,2]=rho2-rho1
    out[:,3]=(velp2+velp1)/2.0
    out[:,4]=(vels2+vels1)/2.0
    out[:,5]=(rho2+rho1)/2.0
    modelAVOAkiRichards3(out)
    modelFattiRpRs(out)
    return out

#class blockLithology(self):
    

###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 09-08-2012

# File Name: ricker.py
# Synopsis:
# Create a ricker wavelet.

import numpy as np

def makeMirrorTime(length,dt):
    return np.arange(-length*dt/2,length*dt/2+dt,dt)

def ricker(length,dt,f):
    '''
    Create an analytical ricker wavelet with a dominant frequency of f.
    Len in samples, dt im mSec, f in Hertz
    '''
    time = np.arange(0,length/2.0*dt-dt,dt)/1000.0
    wave = (1-2*np.pi*np.pi*f*f*time*time)*np.exp(-np.pi*np.pi*f*f*time*time)
    ns=int(len(time)*2)
    trace = np.zeros(ns,float)
    for i in range(0,int(ns/2)):
        trace[ns/2+i]=wave[i]
        trace[ns/2-i]=wave[i]
    return trace
    

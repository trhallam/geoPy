###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 30-07-2015

# File Name: funcFilter.py
# Synopsis:
# Create many types of filters and then applies them to time series.

import numpy as np

def makeLowPass(maxFreq,df,highPass,highCut):
    '''
    Create a low pass filter amplitude spectrum.
    '''
    freqs=np.arange(0,maxFreq,df)
    spect=np.ones(len(freqs))
    m=-1./(highCut-highPass)
    c=1.-(m*highPass)
    i=0
    print(m,c)
    for fq in freqs:
        if fq <= highPass:
            spect[i]=1
        if fq > highPass and fq < highCut:
            spect[i]=m*fq+c
        if fq >= highCut:
            spect[i]=0.
        i=i+1
    return freqs,spect
    
def makeHighPass(maxFreq,df,lowCut,lowPass):
    '''
    Create a high pass filter amplitude spectrum.
    '''
    freqs=np.arange(0,maxFreq,df)
    spect=np.ones(len(freqs))
    m=1./(lowPass-lowCut)
    c=1.-(m*lowPass)
    i=0
    for fq in freqs:
        if fq <= lowCut:
            spect[i]=0
        if fq < lowPass and fq > lowCut:
            spect[i]=m*fq+c
        if fq >= lowPass:
            spect[i]=1.
        i=i+1
    return freqs,spect    
    
def makeBandPass(maxFreq,df,lowCut,lowPass,highPass,highCut):
    '''
    Create a simple bandpass filter.
    '''
    freq,lp=makeLowPass(maxFreq,df,highPass,highCut)
    freq,hp=makeHighPass(maxFreq,df,lowCut,lowPass)
    return freq,lp*hp
    
def transAmpSpec(ar,delta,t='forward'):
    ns=len(ar)

    if t=='forward':
        return np.abs(np.fft.rfft(ar).real), \
               np.fft.fftfreq(ns-1,d=delta/1000.0)[0:ns/2-1]
    if t=='backwards':
        print('ns:',ns)
        print(ns/2,ns,ns/2,ns)
        print(ns,ns*2,0,ns+1)
        tAmp=np.zeros(ns*2)
        tAmp[ns/2+1:ns+1]=np.fft.ifft(ar).real[ns/2:ns]
        tAmp[ns:ns*2]=np.flipud(tAmp[1:ns+1])
        return tAmp
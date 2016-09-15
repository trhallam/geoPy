# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 2016

@author: tony
"""

"""Distribution Models for use in widget"""

from scipy.stats import norm
import numpy as np

def curveNormal(data):
    #Create X values for PDF calc    
    x = np.linspace(xmin,xmax,1000)
    #calculate PDF
    mu, std = norm.fit(data)
#    p = 

def main():
    import matplotlib.pyplot as plt
    print ("Simple Tests")
    data = norm.rvs(10.0, 2.5, size=500)
    #print(data)
    mu, std = norm.fit(data)
    
    print(mu, std)
    
    plt.hist(data, bins=20, normed=True)

    x = np.linspace(0,20,1000)
    p = norm.pdf(x, mu, std)
    q = norm.sf(x, mu, std)

    plt.plot(x, p, 'k', linewidth=2)    
    plt.plot(x, q, 'r', linewidth=2)

if __name__ == "__main__":
    main()
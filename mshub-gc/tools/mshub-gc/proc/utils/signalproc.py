#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Utility functions for MS processing
"""

import numpy as np


def smooth1D(x,y,window=10,method='loess',weighting='tri-cubic'):
    
    """
    Performs fast smoothing of evenly spaced data using moving loess, lowess or average 
    filters.  
    
    References:
        [1] Bowman and Azzalini "Applied Smoothing Techniques for Data Analysis" 
        Oxford Science Publications, 1997.
    
    Args: 
        x: Uniformly spaced feature vector (eg mz or drift time). 
        y: Array of intensities. Smmothing is computed on flattened array of 
            intensities.
        method: Smoothing method {'lowess','loess',or 'average'}, by default 'loess'.
        window: Frame length for sliding window [10 data points, by default].
        weighting: Weighting scheme for smoothing {'tricubic' (default), 'gaussian' or 'linear'}.
             
    Returns:
        yhat: Smoothed signal.
    """ 
    
    from scipy import signal
    from scipy import linalg
   
    leny       = len(y)
    halfw   = np.floor((window/2.))
    window  = int(2.*halfw+1.)
    x1 = np.arange(1.-halfw, (halfw-1.)+1)

    if weighting == 'tri-cubic':
        weight = (1.-np.divide(np.abs(x1), halfw)**3.)**1.5
    elif weighting == 'gaussian':
        weight = np.exp(-(np.divide(x1, halfw)*2.)**2.)  
    elif weighting == 'linear':
        weight = 1.-np.divide(np.abs(x1), halfw)
        
    if method == 'loess':
        V = (np.vstack((np.hstack(weight), np.hstack(weight*x1), np.hstack(weight*x1*x1)))).transpose()
        order = 2
    elif method == 'lowess':
        V = (np.vstack((np.hstack((weight)), np.hstack((weight*x1))))).transpose()
        order = 1        
    elif method =='average':
        V = weight.transpose()
        order = 0    
   
    #% Do QR decomposition
    [Q, R] = linalg.qr(V,mode='economic')
    
    halfw = halfw.astype(int)
    alpha = np.dot(Q[halfw-1,], Q.transpose())
    
    yhat  = signal.lfilter(alpha*weight,1,y)
    yhat[int(halfw+1)-1:-halfw] = yhat[int(window-1)-1:-1]

    x1 = np.arange(1., (window-1.)+1)
    if method == 'loess':
        V = (np.vstack((np.hstack(np.ones([1, window-1])), np.hstack(x1), np.hstack(x1*x1)))).transpose()
    elif method == 'lowess':
        V = (np.vstack((np.hstack(np.ones([1, window-1])), np.hstack(x1)))).transpose()
    elif method =='average':
        V = np.ones([window-1,1])
    
    
    for j in np.arange(1, (halfw)+1):
        #% Compute weights based on deviations from the jth point,
        if weighting == 'tri-cubic':
            weight = (1.-np.divide(np.abs((np.arange(1, window)-j)), window-j)**3.)**1.5
        elif weighting == 'gaussian':
            weight = np.exp(-(np.divide(np.abs((np.arange(1, window)-j)), window-j)*2.)**2.)
        elif method =='linear':
            weight = 1.-np.divide(np.abs(np.arange(1,window)-j), window-j)
        
        W = (np.kron(np.ones((order+1,1)),weight)).transpose();
        [Q, R] = linalg.qr(V*W, mode='economic')
    
        alpha = np.dot(Q[j-1,], Q.transpose())
        alpha = alpha*weight
        yhat[int(j)-1] = np.dot(alpha, y[:int(window)-1])
        yhat[int(-j)] = np.dot(alpha, y[np.arange(leny-1,leny-window,-1,dtype=int)])

    return yhat
    
def get_threshold(X, nbins=''):
   
    """
    Computes an optimal intensity threshold that can be used to separate noisy 
    from useful features.   
    
    References: 
        N Otsu, "A threshold selection method from gray-level histogram, 
        IEEE Trans on System Man Cybernetics 9 (1979), no 1, 62-66.
        
    Args:    

        X: Array of intensities with the threshold calculated over flattened array of intensities.    
         
        nbins: The number of bins for histogram construction. 
        
    Returns:
    
        tval: threshold value.  
        
    """
    
    if not nbins:
       nbins = int(round(np.sqrt(len(X))))
        
    [h,hvals] = np.histogram(X[:],nbins);
    L    = len(h)
    i    = np.arange(1., (L)+1)
    A    = np.cumsum(h)
    B    = np.cumsum((h*i))
    u    = B/A
    tmp  = A[int(L)-1]-A
    v    = (B[int(L)-1]-B)/(tmp+(tmp == 0))
    F    = A*(A[int(L)-1]-A)*(u-v)**2.
    tbin = F.argmax()
    tval = hvals[tbin]-(hvals[1]-hvals[0])*0.5
    return tval
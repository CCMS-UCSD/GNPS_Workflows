# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 15:56:30 2017

Quick correlation coefficient calculation for pair-wise and all vs all
correlation calculation for two sets of measurements, x and y.

NumPy based.

In both x and y rows correspond to variables and columns to measurements

x and y must be NumPy arrays. 

Number of measurements per variable must be equal between x and y.

correlate_all(x, y) returns all combinations of correlations between 
x and y variables as a 2D matrix. 

correlate_pairwise(x, y) returns correlation coefficiens for pair-wise 
combinations variables from x and y as a 1D matrix and thus the number 
of variables (rows) should be equal between the two. 


@author: Dr. Ivan Lapongov
"""

import numpy as np;

def correlate_all(x, y):
    """
    Calculate correlation coefficients for all pair-wise combinations of x[i, :]
    and y[j, :] and return as a matrix Corr[i,j]. 
    Number of columns for x and y must be the same. 
    x and y must be 1D or 2D NumPy arrays. 
    Args: x, y - NumPy arrays of measurements. Rows correspond to variables, columns
                to their measurements
    Returns:
        Corr  - 2D NumPy matrix, where 
                Corr[i, j] = cov(x[i, :], y[j, :]) /
                sqrt(cov(x[i, :], x[i, :]) * cov(y[j, :], y[j, :]))
                
                where cov stands for covariance
    
    """

    if len(x.shape) > 2:
        raise ValueError('X must be one or two-dimensional matrix!')
    elif len(x.shape) == 1:
        x = x.reshape(1, x.shape[0]);
    
    if len(y.shape) > 2:
        raise ValueError('Y must be one or two-dimensional matrix!')    
    elif len(y.shape) == 1:
        y = y.reshape(1, y.shape[0]);
    
    if x.shape[1] != y.shape[1]:
        raise ValueError('Both datasets should have equal number of columns!')
    
    mx = np.mean(x, axis = 1);
    my = np.mean(y, axis = 1);

    x = np.subtract(x, mx.reshape(mx.shape[0], 1));
    y = np.subtract(y, my.reshape(my.shape[0], 1));

    self_cov_x = np.sum(np.multiply(x, x), axis = 1);
    self_cov_y = np.sum(np.multiply(y, y), axis = 1);
    
    return np.divide(np.dot(x, y.transpose()),
                     np.sqrt(
                             np.multiply(
                                         np.multiply(
                                                     np.ones((x.shape[0], y.shape[0]), dtype = np.float64),
                                                     self_cov_x.reshape(self_cov_x.shape[0], 1)
                                                     ),
                                         self_cov_y
                                         )                                         
                            )
                    )
    
    


def correlate_pairwise(x, y):
    """
    Calculate correlation coefficients for all pairs of x[i, :]
    and y[i, :] and return as a 1D matrix or their pairs.
    Number of columns and rows for x and y must be the same. 
    x and y must be 1D or 2D NumPy arrays. 
    Args: x, y - NumPy arrays of measurements. Rows correspond to variables, columns
                to their measurements
    Returns:
        Corr  - 1D NumPy matrix, where 
        Corr[i] = cov(x[i, :], y[i, :])/
                  sqrt(cov(x[i, :], x[i, :]) * cov(y[i, :],y[i, :]))
                  
                  where cov stands for covariance
    
    """

    if x.shape != y.shape:
        raise ValueError('Both datasets should have identical dimensions!');

    if len(x.shape) > 2:
        raise ValueError('X must be one or two-dimensional matrix!')
    elif len(x.shape) == 1:
        x = x.reshape(1, x.shape[0]);
    
    if len(y.shape) > 2:
        raise ValueError('Y must be one or two-dimensional matrix!')    
    elif len(y.shape) == 1:
        y = y.reshape(1, y.shape[0]);
    
    mx = np.mean(x, axis = 1);
    my = np.mean(y, axis = 1);
    
    x = np.subtract(x, mx.reshape((mx.shape[0], 1)));
    y = np.subtract(y, my.reshape((my.shape[0], 1)));
    
    self_cov_x = np.sum(np.multiply(x, x), axis = 1);
    self_cov_y = np.sum(np.multiply(y, y), axis = 1);

    return np.divide(
                    np.sum(np.multiply(x, y), axis = 1), 
                    np.sqrt(np.multiply(self_cov_x, self_cov_y)));
        


if __name__ == '__main__':
    
    
    d1 = np.array([[0,1,2,3,4,5],[3,4,4,5,3,5]]);
    d2 = np.array([[0,1,2,3,4,5],[3,3,4,4,3,5]]);
    
    corr = correlate_pairwise(d1, d2)
    
    print(np.corrcoef(d1[0,:], d2[0,:])[0, 1], corr[0])
    print(np.corrcoef(d1[1,:], d2[1,:])[0, 1], corr[1])
    
    d1 = np.array([[1,2,3,4,5,6],[2,3,4,5,6,7], [2,3,3,3,4,3]])
    d2 = np.array([[1,2,4,5,6,7],[2,1,0,-1,-2,-3]])
    
    corr = correlate_all(d1, d2);
    
    print(np.corrcoef(d1[0, :], d2[0, :])[0,1], corr[0, 0]);
    print(np.corrcoef(d1[0, :], d2[1, :])[0,1], corr[0, 1]);
    print(np.corrcoef(d1[1, :], d2[0, :])[0,1], corr[1, 0]);
    print(np.corrcoef(d1[1, :], d2[1, :])[0,1], corr[1, 1]);
    print(np.corrcoef(d1[2, :], d2[0, :])[0,1], corr[2, 0]);
    print(np.corrcoef(d1[2, :], d2[1, :])[0,1], corr[2, 1]);
    
    corr = correlate_all(d1[0, :], d2[0, :])
    print(corr)
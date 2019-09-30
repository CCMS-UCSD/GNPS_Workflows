# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:18:37 2017

@author: Dr. Ivan Laponogov

Read/Write utf_8 string to/from HDF5 format

"""

import numpy as np;
import sys;
from proc.utils.printlog import printlog, start_log, stop_log, LoggingException;

python_version = sys.version_info.major;

class WrongHDF5Input(LoggingException):
    pass


def _write_string(s, string_dataset, utf_8_dataset, overwrite, index):
    if python_version == 2:                                  
        ba = np.array(bytearray(s.encode('utf-8')));
    else:
        ba = np.array(list(bytes(s.encode('utf-8'))));
    
    
    if overwrite:
        if index >= string_dataset.shape[0]:
            i = string_dataset.shape[0];
        else:
            i = index;
    else:
        i = string_dataset.shape[0];
    
    ii = utf_8_dataset.shape[0];
    jj = ii + ba.shape[0];
        
    string_dataset.resize((i+1, 2))
    utf_8_dataset.resize((jj,));
    
    string_dataset[i, 0] = ii;
    string_dataset[i, 1] = jj;
    
    utf_8_dataset[ii:jj] = ba[:];


def _read_string(utf_8_dataset, ii, jj):
    if python_version == 2:   
        return str(bytearray(utf_8_dataset[ii:jj].tolist()));
    else:
        return str(bytes(list(utf_8_dataset[ii:jj])).decode('utf-8'));

def h5write_strings(string_dataset, utf_8_dataset, strings, overwrite = False):
    """
        Writes strings from strings list to open HDF5 string_dataset. 
    string_dataset should have a shape of (X, 2), where X will be the total 
    number of strings to be written. In no overwrite mode is set, 
    the dataset will automatically be resized - do
    not specifically resize it prior to calling this function, unless you are 
    overwriting the existing strings!

    utf_8_dataset is the array that stores byte string data.

    Both input arrays should be open for writing.

    strings is a list of strings or a string to write to HDF5.
    
    Args:
        string_dataset - open dataset/numpy array of indeces of starting/ending
        positions of the string bytes in utf_8_dataset
        utf_8_dataset - open dataset/numpy array of string bytes
        strings - list of strings or a string
        overwrite - whether to overwrite existing or add new strings
    
    Returns:
        None
    
    """

    if len(string_dataset.shape) != 2:
        raise WrongHDF5Input('string_dataset should have shape len of 2! %s found instead!'%len(string_dataset.shape));
    
    if string_dataset.shape[1] != 2:
        raise WrongHDF5Input('string_dataset should have second dimension length of 2! %s found instead!'%len(string_dataset.shape[1]));
        
    if isinstance(strings, list):
        for i in range(len(strings)):
            _write_string(str(strings[i]), string_dataset, utf_8_dataset, overwrite, i);
    else:
        _write_string(str(strings), string_dataset, utf_8_dataset, overwrite, 0);
    


def h5read_strings(string_dataset, utf_8_dataset):
    """
        Reads strings from open HDF5 string_dataset. string_dataset should 
    have a shape of (X, 2), where X is the number of strings to be read. 
    
    utf_8_dataset is the array that stores byte string data.

    Both input arrays should be open for reading.
    
    Args:
        string_dataset - open dataset/numpy array of indeces of starting/ending
        positions of the string bytes in utf_8_dataset
        utf_8_dataset - open dataset/numpy array of string bytes
    
    Returns:
        empty string if no strings are read
        string if only one string is read
        list of strings if two or more strings are read
    
    """
    result = [];
    
    if len(string_dataset.shape) != 2:
        raise WrongHDF5Input('string_dataset should have shape len of 2! %s found instead!'%len(string_dataset.shape));
    
    if string_dataset.shape[1] != 2:
        raise WrongHDF5Input('string_dataset should have second dimension length of 2! %s found instead!'%len(string_dataset.shape[1]));
        
    for i in range(string_dataset.shape[0]):
        ii = int(string_dataset[i, 0]);
        jj = int(string_dataset[i, 1]);
        result.append(_read_string(utf_8_dataset, ii, jj));
    
    if len(result) == 0:
        return ''
    if len(result) == 1:
        return result[0]
    else:
        return result;
        
        
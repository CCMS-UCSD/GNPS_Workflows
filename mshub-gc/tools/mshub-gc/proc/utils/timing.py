# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 12:48:32 2017

@author: Dr. Ivan Laponogov
"""
#===========================Import section=================================

#Importing standard and external modules
import time;
import os;
import sys;

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path)

#Import local/internal modules
from proc.utils.printlog import printlog;

#==========================================================================
#From here the main code starts


__dttime = {'default':time.time()};

def tic(id_tic = 'default'):
    """
    Records the time it was called thus starting timing.
    
    Args:
        id_tic: string or number to be used to identify this starting point. 
        Default: 'default'
    
    """
    global __dttime;
    __dttime[id_tic] = time.time();
    
def toc(id_tic = 'default', printing = True):
    """
    Returns and prints (optionally) the number of seconds that passed since 
    corresponding tic(id) was called.
    
    Args:
        id_tic:   string or number to be used to identify corresponding starting
                  point. Default: 'default'.
        printing: boolean, determines if the number of elapsed seconds is 
                  printed. Default: True
                 
    Returns:
        number of seconds that passed since corresponding tic(id) was called as
        float.
    """
    global __dttime;

    try:
        t = time.time() - __dttime[id_tic];
    except:
        printlog('tic "%s" not found! Did you forget to call tic(%s)?'%(id_tic, id_tic));
        return 0.0;
    
    if printing:
        printlog('%s seconds'%t)
    return t;
    
    
    
if __name__ == "__main__": 
    tic(1);
    time.sleep(1);
    toc();tic('2')
    time.sleep(1);
    toc(1);
    toc('2');
    toc(2)
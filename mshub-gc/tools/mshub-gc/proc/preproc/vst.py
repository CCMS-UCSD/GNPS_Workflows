# -*- coding: utf-8 -*-
"""
*******************************************
Variance Stabilizing Transformation Module
*******************************************

The module is designed to account for heteroscedastic noise structure 
characterized by increasing variance as a function of increased signal 
intensity. This procedure is essential to make sure that both small and large 
peaks have the same "technical" variance for downstream statistical analysis 
or visualization.    

run python.exe vst.py --help to get info about parameters of the script

Project:                        BASIS
License:                        BSD
Chief project investigator:     Dr. Kirill Veselkov
Lead developer:                 Dr. Kirill Veselkov 
 
References:

    [1] Veselkov KA, et al. (2011) Optimized preprocessing of ultra-
    performance liquid chromatography/mass spectrometry urinary metabolic 
    profiles for improved information recovery. Anal Chem 83(15):5864-5872.
    
    [2] Veselkov KA, et al. (2014), Chemo-informatic strategy for imaging mass 
    spectrometry-based hyperspectral profiling of lipid signatures in 
    colorectal cancer. PNAS, 111: 1216-122. 
 
"""
#===========================Import section=================================

#Importing standard and external modules
import os
import sys;
import h5py
import numpy as np
import traceback
import time

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path)

#Import local/internal modules
import basis.io.manageh5db as mh5

from basis.utils.typechecker import is_string, is_number
from basis.utils.cmdline import OptionsHolder, AttributeCollection;

from basis.procconfig import VST_options;

from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts


def do_vst(dbprocpath='', method='', params = ''):
    
    """
    **Performs inter-sample normalization to account for overall intensity varation between tissue samples.**
     
    Args:
                
        dbprocpath:  The path to a hdf5-based msi database for storage and organization of pre-processed MSI data. 
                     The variance stabilizing transformation needs to be applied after peak alignment, lock
                     mass correction and normalization steps.
                        
        
        method:      The choice of a variance stabilizing transformation method {``started-log`` (default)}
                     Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for variance stabilizing transformation method. The ``offset`` parameter is added by prior to performing started-log transformation
                         
    """
    
    if is_string(dbprocpath) and os.path.exists(dbprocpath):
        datasets = mh5.get_dataset_names(dbprocpath,dataset_names=[])
        if not datasets:
            printlog(dbprocpath + ' database file doesn''t contain any MSI datasets')
            return
    else:
        printlog(str(dbprocpath) + ' database file is not found')
        return
                              
    #  Exctract all variance stabilizing transformation parameters if available
    objattrs = mh5.load_preproc_obj(dbprocpath,'Variance stabilizing transformation')
    if isinstance(objattrs,dict):
        method = objattrs['method']
        params = objattrs['params']
        isdbparam = True
    else:
        isdbparam = False
    
        
    printlog('\n\n\n' '...Initializing variance stabizing transformation procedure... ')
    
    h5proc = h5py.File(dbprocpath,'a')
    
    datasets = np.unique(datasets)
    # apply variance stabilizing transformation
    for datasetid in datasets:
        try:
            printlog('\n'+os.path.basename(dbprocpath) +": Preparing for variance stabilizing transformation " + datasetid)
            X  = mh5.load_dataset(h5proc,datasetid+'/Sp')
            ncmz,nobs = X.shape
            
            # apply vst     
            X  =  vst(X,method,params)
            
            # save dataset
            mh5.save_dataset(h5proc,datasetid+'/Sp',X)
            
            printlog("The variance stabizing transformation of dataset: " +datasetid+" has successfully completed!")
        except Exception as inst:
            printlog("The variance stabizing transformation of dataset: " +datasetid+": has failed!")
            printlog(inst)
            traceback.print_exc()
            h5proc[datasetid].attrs['is_OK'] = False;
            
        
    
    # pickle and save vst parameters into the hdf5 database file  
    #To be reworked.....
    VSTObj=AttributeCollection();
    VSTObj.method=method;
    VSTObj.params=params;
    VSTObj.do='yes';
    VSTObj.description='Variance Stabilizing Transformation Settings'
    
    
    if isdbparam==False:
        mh5.save_preproc_obj(h5proc,VSTObj) 
        vstattr = vars(VSTObj)
        mh5.save_preproc2matlab(h5proc,vstattr['do'],4, 
                                vstattr['description'], vstattr['method'], vstattr['params'])  
                                     
           
    h5proc.close()
     
    return
    
def vst(X,method,params):
    """
    **Perform variance stabilizing transformation.**

    Args:
        
        X: MSI dataset (number of m/z features, number of rows, number of columns).
              
        method:      The choice of a variance stabilizing transformation method {``started-log`` (default)}
                     Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for variance stabilizing transformation method. The ``offset`` parameter is added by prior to performing started-log transformation.               
        
     
    Returns:
    
        X: variance stabilized dataset.
    """
    #warnings.filterwarnings("ignore")
          
    methodselector = {'started-log': started_log}
    
    vstfunc  = methodselector.get(method);
    
    X  = vstfunc(X,params)          
    return X 
    
def started_log(X,params):
    """
    **Performs started-log variance stabilizing transformation.**

    Args:
        
        X: MSI dataset (number of m/z features, number of rows, number of columns).
              
        params:     The set of parameters for variance stabilizing transformation method. The ``offset`` parameter is added by prior to performing started-log transformation.               
        
     
    Returns:
    
        X: variance stabilized dataset.
        
    """
    
    offset = params['offset']
    if not is_number(params['offset']):
        offset=1.
    X = np.log(X+offset)
    return X

def pylog(X,params):
    X = np.log(X+1)
    return X
    

if __name__ == "__main__": 
    settings=OptionsHolder(__doc__, VST_options);
    settings.description='Variance Stabilizing Transformation Settings';
    settings.do='yes';
    printlog(settings.program_description);
    #Parse command line parameters
    try:
        settings.parse_command_line_args()   
    except Exception as inst:
        printlog('!!! Error in command line parameters: !!!');
        printlog(inst);
        printlog('\nRun python ' + sys.argv[0] + ' --help for command line options information!');
        sys.exit(-1)

    parameters = settings.parameters;
    if parameters['logfile'] != '':
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'), verbosity_level = parameters['verbose']);
        printlog(settings.program_description, print_enabled = False);

    printlog('Started on %s ...'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    
    printlog(settings.format_parameters());
    
    do_vst(dbprocpath=settings.parameters['h5dbname'], method=settings.parameters['method'], params=settings.parameters['params']);

    printlog('\nFinished on %s.'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    printlog(settings.description_epilog);
    stop_log();

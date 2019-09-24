## -*- coding: utf-8 -*-
"""
*********************************
Intra-sample Normalization Module
*********************************

The module is designed to account for overall intensity (pixel to pixel) 
variation between spectra within individual datasets. This unwanted variation 
can be caused by a variety of reasons, including heterogeneous matrix 
deposition (e.g. MALDI) or differences in tissue thickness within a tissue 
sample.   

See also inter-sample normalization module to account for global intensity 
differences between samples.

run python.exe intranorm.py --help to get info about parameters of the script

  
References:

    [1] Veselkov KA, et al. (2011) Optimized preprocessing of ultra-
    performance liquid chromatography/mass spectrometry urinary metabolic 
    profiles for improved information recovery. Anal Chem 83(15):5864-5872.
    
    [2] Veselkov KA, et al. (2014), Chemo-informatic strategy for imaging mass 
    spectrometry-based hyperspectral profiling of lipid signatures in 
    colorectal cancer. 
    PNAS, 111: 1216-122. 
 
"""

#===========================Import section=================================

#Importing standard and external modules
import h5py
import numpy as np
import os
import time
import traceback
import sys;
import warnings

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

import basis.io.manageh5db as mh5

from basis.procconfig import IntraNorm_options

from basis.utils.typechecker import is_string, is_number
from basis.utils.cmdline import OptionsHolder, AttributeCollection;

#==========================================================================
#From here the main code starts

def do_normalize(dbprocpath='', method='', params = {}, mzrange=''):
    
    """
    **Performs intra-sample normalization module to account for overall intensity (pixel to pixel) variation between spectra within individual datasets.**
     
    See also inter-sample normalization to account for overall intensity varation between tissue samples. 
    
    Args:
                    
        dbprocpath:  The path to a hdf5-based msi database for storage and organization of pre-processed MSI data. 
                     The intra/inter-sample normalization procedures are applied after peak alignment and lock
                     mass correction steps.
                        
        
        method:     The choice of an intra-sample normalization method {``median fold change`` (default), ``mean`` or ``median``}
                    Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for intra-sample normalization method. The median fold change normalization requires the refence dataset with respect to which the fold intensity changes of other datasets are
                    calculated, ``mean`` by default. The ``offset`` parameter disregards peak intensity smaller that its value. 
                    ``{'reference': 'mean', 'offset': 0}`` by default for median fold change 
                    
        
        mzrange:    [mzmin mzmax] - the mass-to-charge ratio (m/z) range desired to be processed. If not specified, the full mz range is used. 
         
    """
                    
    #printlog(dbprocpath)             
    if  is_string(dbprocpath) and os.path.exists(dbprocpath):
        datasets = mh5.get_dataset_names(dbprocpath,dataset_names=[])
        if not datasets:
            printlog(dbprocpath + ' database file doesn''t contain any MSI datasets')
            return
        #printlog(datasets)
    else:
        printlog(str(dbprocpath) + ' database file is not found')
        return
                               
    isdbparam = False;
    
    # configure intra-normalization parameters
    #  Exctract all inter-sample normalization parameters if available
    objattrs = mh5.load_preproc_obj(dbprocpath,'Intra-sample normalization')
    if isinstance(objattrs,dict):
        method = objattrs['method']
        params = objattrs['params']
        isdbparam = True
    else:
        isdbparam = False
    
    params['adjust']='yes';
    
    printlog('\n\n\n' '...Initializing intra-sample normalization procedure... ')
    
    h5proc = h5py.File(dbprocpath,'a')
    for datasetid in datasets:
        try:
            printlog('\n'+os.path.basename(dbprocpath) +": Preparing for intra-sample normalization " + datasetid)
            
            # import data from the hdf5 database file
            # X [number of features, number of rows, number of columns] - opposite to matlab
            mz = mh5.load_dataset(h5proc,datasetid+'/mz')
            X  = mh5.load_dataset(h5proc,datasetid+'/Sp') 
            #printlog(X)
            
            # perform intra-sample normalization            
            X  = intranorm(X, method, params, mzrange, mz)
            
            # re-write data-set in the hdf5 database file     
            mh5.save_dataset(h5proc,datasetid+'/Sp', X)
            
            printlog("The intra-sample normalization of dataset: " +datasetid+" has successfully completed!")
        except Exception as inst:
            printlog("The intra-sample normalization of dataset: " +datasetid+": has failed!")
            printlog(inst)
            traceback.print_exc()
            h5proc[datasetid].attrs['is_OK'] = False;
            
            
    
    # pickle and save intra-sample normalization parameters
    #!----------------------------------------------
    #Needs reworking!
    IntraNormObj=AttributeCollection();
    IntraNormObj.method=method;
    IntraNormObj.params=params;
    IntraNormObj.do='yes';
    IntraNormObj.description='Itranormalization Settings'
    
    if isdbparam==False:
        mh5.save_preproc_obj(h5proc,IntraNormObj)
        intranormattr = vars(IntraNormObj)
        mh5.save_preproc2matlab(h5proc,intranormattr['do'],2, 
                                intranormattr['description'], intranormattr['method'], intranormattr['params'])          

    h5proc.close()
     
    return


def intranorm(X,method,params,mzrange='',mz=''):
    """
    **Perform intra-sample normalization.**
    
    Args:
        
        X: MSI dataset (number of m/z features, number of rows, number of columns).
              
        method:      The choice of an intra-sample normalization method {``median fold change`` (default), ``mean`` or ``median``}
                     Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for inter-sample normalization method. The median fold change normalization requires the refence profile with respect to which the fold intensity changes are
                    calculated, ``mean`` by default. The ``offset`` parameter disregards peak intensity smaller that its value. 
                    ``{'reference': 'mean', 'offset': 0}`` by default for median fold change 
                    
        
        mzrange:    [mzmin mzmax] - The mass-to-charge ratio (m/z) range desired to be processed. If not specified, the full data range will be used. 
        
        mz: The mass to charge feature vector.

    Returns:
        
        X: normalized dataset
    """
    warnings.filterwarnings("ignore")
          
    ## select appropriate normalization method    
    methodselector = {'mean': mean, 
                      'median': median, 
                      'mfc': mfc};
              
    normfunc  = methodselector.get(method);
    
    ## prepare data for normalization    
    nmz,nobs = X.shape
    Xn = X    
    try: 
        if (len(mzrange)>0) and (len(mz)>0):
            Xn = X[(mz>mzrange[0]) & (mz<mzrange[1]),:]
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        
    offset = params['offset'];
    
    if is_number(offset):
        Xn[Xn<=offset]   = 0
    
    Xn[np.isnan(Xn)] = 0    
    
    ## ignore mz features with all zeros or nans
    sumX      = np.nansum(Xn,axis=1)
    Xn        = Xn[sumX!=0,:]
    Xn[Xn==0] = np.nan
    
    ## get normalization factors for each spectrum  
    scf,refX = normfunc(Xn,params)
    scf = scf.reshape(1,nobs)
    scf[np.isnan(scf)] = 1
    scf[scf==0] = 1
    scf = np.divide(scf,np.nanmedian(scf))
    
    ## estimate expected range of scaling factors and adjust the outlying ones
    if params['adjust']=='yes':
        logscf     = np.log(scf[scf>0]);
        stdlogscf  = 1.4826 * np.median(abs(logscf - np.median(logscf)))
        scf[scf<np.exp(-stdlogscf*3)] = np.exp(-stdlogscf*3)
        scf[scf>np.exp(+stdlogscf*3)] = np.exp(+stdlogscf*3)
    
    ## divide each spectrum with its estimated normalization factor    
    scf = scf.reshape(1,nobs)    
    X = X/scf
    #X = X.reshape(nmz,nrows,ncols)        
    return X
    
def mean(X):
    """**Caclulates mean value per spectrum, **mean intra-sample normalization.**
    Args:
        X: MSI dataset (number of m/z features x number of spectra )
    Returns:
        scfactors: normalization factors.
    """
              
    scfactors = np.nanmean(X,axis=0)
    refX = []
    return scfactors, refX

def median(X,params):
    """**Caclulates median value per spectrum, **mean intra-sample normalization.**
    Args:
        X: MSI dataset (number of m/z features x number of spectra )
    Returns:
        scfactors: normalization factors
    """
              
    scfactors = np.nanmean(X,axis=0)
    refX = []
    return scfactors, refX
    
def mfc(X,params):
    """**Caclulates median fold change value, **median fold change intra-sample normalization.**
    Args:
        X: MSI dataset (number of m/z features x number of spectra )
    Returns:
        scfactors: normalization factors
    """
    
    ref = params['reference']
    if is_string(ref) and ref=='mean':
        refX = np.nanmean(X,axis=1)
    elif is_string(ref) and ref =='median':
        refX = np.nanmedian(X,axis=1)
    else:
        refX=ref
    
    refX[refX==0]=np.nan
    refX = refX.reshape(len(refX),1)
    scfactors = np.nanmedian(X/refX,axis=0)
    return scfactors, refX
        
if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, IntraNorm_options);
    settings.description='Itranormalization Settings';
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
    
    do_normalize(dbprocpath=settings.parameters['h5dbname'],\
                 method=settings.parameters['method'],\
                 params = settings.parameters['params'],\
                 mzrange=[settings.parameters['min_mz'], settings.parameters['max_mz']]);
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog)
    stop_log();
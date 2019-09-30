# -*- coding: utf-8 -*-
"""
*********************************
Inter-sample Normalization Module
*********************************

The module is designed to account for overall intensity differences between 
MSI datasets of multiple tissue samples. This unwanted variation can be caused
by a variety of reasons, including  differences in sample preparation steps or 
tissue section thickness.   

See also intra-sample normalization module to account for overall intensity 
(pixel to pixel) variation between spectra within individual datasets.


run python.exe internorm.py --help to get info about parameters of the script


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
import warnings
import sys;

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path)

#Import local/internal modules
import basis.io.manageh5db as mh5

from basis.preproc import intranorm

from basis.procconfig import InterNorm_options;

from basis.utils.cmdline import OptionsHolder, AttributeCollection;
from basis.utils.typechecker import is_string, is_number

from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts

def do_normalize(dbprocpath='', method='', params = '', mzrange=''):
    
    """
    ** Performs inter-sample normalization to account for overall intensity varation between tissue samples.**
     
    Args:
                    
        dbprocpath: The path to a hdf5-based msi database for storage and organization of pre-processed MSI data. 
                    The intra/inter-sample normalization procedures are applied after peak alignment and lock
                    mass correction steps.
                        
        
        method:     The choice of an inter-sample normalization method {"MFC" for median fold change (default), ``mean`` or ``median``}
                    Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for inter-sample normalization method. The median fold change normalization requires 
                    the refence dataset with respect to which the fold intensity changes of other datasets are
                    calculated, ``mean`` by default. The ``offset`` parameter disregards peak intensity smaller that its value. 
                    ``{'reference': 'mean', 'offset': 0}`` by default for median fold change 
                    
        
        mzrange:    [mzmin mzmax] - the mass-to-charge ratio (m/z) range desired to be processed. If not specified, the full mz range is used. 
         
    """
                    
                 
    if is_string(dbprocpath) and os.path.exists(dbprocpath):
        datasets = mh5.get_dataset_names(dbprocpath,dataset_names=[])
        if not datasets:
            printlog(dbprocpath + ' database file doesn''t contain any MSI datasets')
            return
    else:
        printlog(str(dbprocpath) + ' database file is not found')
        return
                              
    #  Exctract all inter-sample normalization parameters if available
    isdbparam = False                          
   
    #!--------------------------------------
    #Needs reworking!
    objattrs = mh5.load_preproc_obj(dbprocpath,'Inter-sample normalization')
    if isinstance(objattrs,dict):
        method = objattrs['method']
        params = objattrs['params']
        gscale = objattrs['gscale']
        isdbparam = True
    else:
        isdbparam = False
        
    
    #printlog(InterNormObj.params)
    
    printlog('\n\n\n' '...Initializing inter-sample normalization procedure... ')
    
    h5proc = h5py.File(dbprocpath,'a')
    
    # derive normalization scaling factors per dataset in an iterative fashion
    refX = []
    passdatasets = []
    for datasetid in datasets:
        try:
            printlog('\n'+os.path.basename(dbprocpath) +": Preparing for inter-sample normalization " + datasetid)
            
            # prepare data
            
            mz = mh5.load_dataset(h5proc,datasetid+'/mz')
            X  = mh5.load_dataset(h5proc,datasetid+'/Sp')
            
            # get dataset specific summary values for estimation of scaling factors
            refx = get_scaling_factors(X, method, params, mzrange, mz)

            refX.append(refx)            
            printlog(os.path.basename(dbprocpath) +": Done... " + datasetid)
            passdatasets.append(datasetid)
        except Exception as inst:
            printlog(os.path.basename(datasetid) + ": Failed...")
            printlog(inst)
            traceback.print_exc()
            h5proc[datasetid].attrs['is_OK'] = False;
            
            
    
    # get scaling factors
    refX=np.transpose(np.squeeze(np.array(refX)))
    if method=='mfc':
        mfcparams = params
        if isdbparam==True:
            normRef = mh5.load_dataset(h5proc,'normRef')
             # use pre-existing reference to get the scaling factors            
            mfcparams['reference'] = normRef    
        scX,normRef = intranorm.mfc(refX,mfcparams)
        
        if isdbparam == False:
            mh5.save_dataset(h5proc,'normRef',normRef)
    else:
        scX  = refX
    
    
    # pickle and save intra-sample normalization parameters  
    if isdbparam==False:
        gscale = np.nanmedian(scX)
        
        # To be reworked properly
        #!------------------------------------
        InterNormObj=AttributeCollection();
        InterNormObj.method=method;
        InterNormObj.params=params;
        InterNormObj.do='yes';
        InterNormObj.description='Iternormalization Settings'
    
        InterNormObj.gscale = gscale
        mh5.save_preproc_obj(h5proc, InterNormObj) 
        internormattr = vars(InterNormObj)
        mh5.save_preproc2matlab(h5proc,internormattr['do'],3, 
                                internormattr['description'], internormattr['method'], internormattr['params'])  
                                
    # maintain original data scale
    scX = scX/gscale
    scX = scX.squeeze()
    scX[np.isnan(scX)] = 1
    scX[scX==0] = 1
    
    # now apply normalization procedure in an iterative fashion, one sample at a time 
    i = 0    
    for datasetid in passdatasets:
        try:
            printlog('\n'+os.path.basename(dbprocpath) +": Performing inter-sample normalization " + datasetid)
            X  = mh5.load_dataset(h5proc,datasetid+'/Sp') 
            X  = X/scX[i]
            # re-write data-set in the hdf5 database file     
            mh5.save_dataset(h5proc,datasetid+'/Sp', X)
            
            printlog("The inter-sample normalization of dataset: " +datasetid+" has successfully completed!")
        except Exception as inst:
            printlog("The inter-sample normalization of dataset: " +datasetid+": has failed!")
            printlog(inst)
            traceback.print_exc()
            h5proc[datasetid].attrs['is_OK'] = False;
            
            
        i = i+1        
    
         
           
    h5proc.close()
     
    return


def get_scaling_factors(X, method, params, mzrange='', mz=''):
    """
    **Caclulates scaling factors for inter-sample normalization procedure.**
    
    Args:
        
        X: MSI dataset (number of m/z features, number of rows, number of columns).
              
        method:      The choice of an inter-sample normalization method {``median fold change`` (default), ``mean`` or ``median``}
                     Additional methods can be added in a modular fashion. 
                    
        params:     The set of parameters for inter-sample normalization method. The median fold change normalization requires the refence profile with respect to which the fold intensity changes are
                    calculated, ``mean`` by default. The ``offset`` parameter disregards peak intensity smaller that its value. 
                    ``{'reference': 'mean', 'offset': 0}`` by default for median fold change 
                    
        mzrange:    [mzmin mzmax] - The mass-to-charge ratio (m/z) range desired to be processed. If not specified, the full data range will be used. 
        
        mz: The mass to charge feature vector.
    
    Returns:
             refX: reference profile or scaling factor for inter-sample normalization.
    """
    warnings.filterwarnings("ignore")
    
    methodselector = {'mean': get_refmean, 
                      'median': get_refmedian, 
                      'mfc': get_refmfc};
              
    normfunc  = methodselector.get(method);
    
    ## prepare data for normalization    
    nmz,nobs = X.shape
    #X  = X.reshape(nmz,nrows*ncols)
    Xn = X    
    try: 
        if (len(mzrange)>0) and (len(mz)>0):
            Xn = X[(mz>mzrange[0]) & (mz<mzrange[1]),:]
    except Exception as inst:
        printlog(inst)
        traceback.print_exc()
        
    offset = params['offset'];

    if is_number(offset):
        Xn[Xn<=offset] = 0
    sumx = np.nansum(Xn,axis=0)
    ## remove spectra with all zeros 
    Xn  = Xn[:,sumx!=0]    
    Xn[Xn==0] = np.nan
        
    refX = normfunc(Xn,params)
    return refX
    
def get_refmean(X,params):
    """
    **Caclulates global median value across all spectra in a dataset, **mean inter-sample normalization.**
    Args:
              X: MSI dataset (number of spectra x number of m/z features)
    """
    refx = np.nanmean(X)
    return refx

def get_refmedian(X,params):
    """
    **Caclulates global median value across all spectra in a dataset, **mean inter-sample normalization.**
    Args:
              X: MSI dataset (number of spectra x number of m/z features)
              """
    refx = np.nanmedian(X)
    return refx
    
def get_refmfc(X,params):
    """
    **Caclulates median profile across all spectra in a dataset, **median fold change inter-sample normalization.**
    Args:
              X: MSI dataset (number of spectra x number of m/z features)
              params: {'reference': 'mean'}, the choice of representative profile profile for median fold change normalization, 'mean' by default. 
    """
    ref = params['reference']
    if ref=='mean':
        refx = np.nanmean(X,axis=1)
    elif ref =='median':
        refx = np.nanmedian(X,axis=1)
    
    refx[refx==0]=np.nan
    refx = refx.reshape(len(refx),1)

    return refx
        
if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, InterNorm_options);   
    settings.description='Iternormalization Settings';
    settings.do='yes';
    settings.gscale=[];
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
    #settings.parameters['h5dbname'] = '/Users/kv/desktop/test/pyproc_data__1928_22_03_2017.h5'
    do_normalize(dbprocpath=settings.parameters['h5dbname'],\
                 method=settings.parameters['method'],\
                 params = settings.parameters['params'],\
                 mzrange=[settings.parameters['min_mz'], settings.parameters['max_mz']]);
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));       
    toc();
    printlog(settings.description_epilog);
    stop_log();

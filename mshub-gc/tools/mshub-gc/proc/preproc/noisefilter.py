# -*- coding: utf-8 -*-
"""

*******************************************************************
Noise filtering module for chromatography - mass spectrometry data
*******************************************************************

The module is designed to adjust for high frequency noise and baseline distortions
of chromatography - mass spectrometry data matrix caused by a variety of 
instrumental and experimental reasons

run python.exe noisefilter.py --help to get info about parameters of the script
"""

#===========================Import section=================================

#Importing standard and external modules
import os
import sys;
import h5py
import numpy as np
import traceback
from scipy.signal import savgol_filter
from scipy import ndimage
import time

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
import proc.io.manageh5db as mh5
from proc.io.manageh5db import LoggingValueError;

from proc.procconfig import NoiseFilter_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts


def do_noisefilter(dbfilepath, smoothmethod='sqfilter', smoothparams = {'window': 5,'degree':3}, 
                   baselinemethod='tophat', baselineparams = {'frame':90},
                   params = {'h5readpath':'/sp2D','h5writepath':'/spproc2D'}, istrain=1):
    
    """
    Performs adjustment for high frequency noise and lower frequency baseline distortions 
    due to a variety of instrumental and experimental reasons
    
    Args:
    
        dbfilepath: a user-specified path to the h5 database file
                    
        smoothmethod: The type of noise filtering method. Default value: 'sqfilter', i.e. the Savitzky-Golay filter.  
        
        smoothparams: The dictionary of parameter arguments for noise filtering method 
        
        baselinemethod: The type of a baseline correction method. Default value: 'tophat', i.e. the top-hat morphological filter.
        
        baselineparams: The dictionary of parameter arguments for baseline correction method          
    """     
    
    params['h5writepath'] = h5Base.correct_h5path(params['h5writepath'])
    params['h5readpath']  = h5Base.correct_h5path(params['h5readpath'])
    dataset_names = mh5.get_dataset_names(dbfilepath,dataset_names=[],pathinh5 = params['h5readpath'][:-1])
    if not dataset_names:
        return

    peak_width = mh5.load_dataset(dbfilepath, params['h5readpath'] + 'peak_width');
    printlog('Loaded min estimated peak width: %s seconds'%peak_width);
    mh5.save_dataset(dbfilepath, params['h5writepath'] + 'peak_width',\
                                 data=peak_width)

        
    if str(smoothparams['window']).lower() == 'auto':
        smoothparams['window'] = peak_width * 0.5;
        printlog('Parameter "window" is set to %s'%smoothparams['window']);
    else:
        try:
            smoothparams['window'] = float(smoothparams['window'])
        except:
            raise LoggingValueError('Error! %s value for parameter "window" cannot be converted to float!'%smoothparams['window'])
            
            

    
    if str(baselineparams['frame']).lower() == 'auto':
        baselineparams['frame'] = peak_width * 15;
        printlog('Parameter "frame" is set to %s'%baselineparams['frame']);
    else:
        try:
            baselineparams['frame'] = float(baselineparams['frame'])
        except:
            raise LoggingValueError('Error! %s value for parameter "frame" cannot be converted to float!'%baselineparams['frame'])
            
        


    if istrain==1:
        rtrange = mh5.load_dataset(dbfilepath, params['h5readpath'] + 'rtrange') 
        if smoothmethod!='none':
            SmoothObject = SmoothFilter(smoothmethod, smoothparams, rtrange)
        else:
            SmoothObject = []
            
        if baselinemethod!='none':
            BaselineObject = BaselineFilter(baselinemethod,baselineparams, rtrange)  
        else: 
            BaselineObject = []
        
            
    elif istrain==0:
        SmoothObject = SmoothFilter()
        SmoothObject.load_procobj(dbfilepath, params['h5readpath'])
        if SmoothObject.method=='':
            SmoothObject = []
        BaselineObject = BaselineFilter()
        if BaselineObject.method=='':
            BaselineObject = []
        BaselineObject.load_procobj(dbfilepath, params['h5readpath'])
        
    filternoise_h5(dbfilepath, dataset_names, SmoothObject, BaselineObject, params)
    
    if istrain==1:
         #save into hdf5 database file
        if (SmoothObject):
            SmoothObject.export(rtrange)
            SmoothObject.save_procobj(dbfilepath,params['h5writepath'])    
        if  (BaselineObject):
            BaselineObject.export(rtrange)
            BaselineObject.save_procobj(dbfilepath,params['h5writepath'])
            
        SmoothObject.save_proc_meta(dbfilepath,params['h5writepath'],params['h5readpath'])
                    
    return
      
        

def filternoise_h5(dbfilepath, datasets, SmoothObject, BaselineObject, params):
    
    if (SmoothObject) and (BaselineObject):
        printlog('\n' + "Preparing for smoothing and baseline correction " + os.path.basename(dbfilepath)+'\n')
        printstring = 'Successfully smoothed, baseline corrected and deposited ->'
    elif (SmoothObject):
        printlog('\n' + "Preparing for smoothing " + os.path.basename(dbfilepath)+'\n')
        printstring = 'Successfully smoothed and deposited ->'
    elif (BaselineObject) ==True:
        printlog('\n' + "Preparing for baseline correction " + os.path.basename(dbfilepath)+'\n')
        printstring = 'Successfully baseline corrected and deposited ->'
    else:
        return
    
    with h5py.File(dbfilepath, 'a') as h5file:
      
        
        i=0
        dataindex = 0    
        for datasetid in datasets:
            dataindex = dataindex + 1        
            try:
                sp2D = mh5.load_dataset(h5file,params['h5readpath'][:-1] + datasetid + '/sp')
                if (SmoothObject):
                    sp2D = SmoothObject.fit(sp2D)
                if (BaselineObject):
                    sp2D = BaselineObject.fit(sp2D)
                    
                mh5.save_dataset(h5file,params['h5writepath'][:-1] + datasetid +'/sp',\
                                 data=sp2D,compression_opts = 5)
                printlog('%s. %s: %s %s%s' %(dataindex, datasetid, printstring, \
                                          os.path.basename(dbfilepath),params['h5writepath'])) 
                i = i + 1
    
                target_gname = params['h5writepath'][:-1] + datasetid;
                source_gname = params['h5readpath'][:-1] + datasetid;
    
                wgroup = h5file[target_gname];
                sgroup = h5file[source_gname];
                    
                wgroup.attrs['is_raw'] = False;
                wgroup.attrs['is_OK'] = True;
                wgroup.attrs['is_processed'] = True;
                wgroup.attrs['is_continuous'] = True;
                wgroup.attrs['is_sample_dataset'] = True;
                wgroup.attrs['parent'] = np.string_(source_gname)
                mh5.copy_meta_over(sgroup, wgroup);
                
                
                
            except Exception as inst:
                printlog('%s. %s: %s'  %(dataindex, datasetid, 'Failed'))  
                printlog(inst)
                traceback.print_exc()
            
    
    
class SmoothFilter(h5Base):
    
    """
    **The container containing the choice of methods and parameters for smoothing 
    of generated intensity matrix from GC-MS data by means of various filters**
    
    Attributes:
       
            method: the method choice for smoothing
            
            params: dictionary of parameter arguments for smoothing 
                                                         
    """   
    
    def __init__(self, method='', params='', rtrange=''):
        super(type(self), self).__init__()
        self.description = 'Intensity smoothing'
        self.method = method

            
        if method=='sqfilter':
            params['window'] = np.ceil(params['window']/rtrange[1])
            params['window'] = (np.floor(params['window']/2))*2 + 1
        self.params = params
              
    def fit(self, ics):       
        
        """
        Performs smoothing of generated intensity matrix from GC-MS data by means of various filters
        
        Args:
        
            ics: ion chromatograms for m/z channels 
                
            method: the method choice for smoothing
            
            params: dictionary of parameter arguments for smoothing 
            
        """  
        
        if self.method=='sqfilter':
            nsp,nmz = ics.shape
            for i in range(nmz):
                ics[:,i] = savgol_filter(ics[:,i] , int(self.params['window']), int(self.params['degree']))
            ics[ics<=0] = 0
        
        return ics
    
    def export(self,rtrange):
        self.params['window'] = self.params['window']*rtrange[1]
           

class BaselineFilter(h5Base):

    """
    
    **The container containing the choice of methods and parameters for baseline correction 
    of generated intensity matrix from GC-MS data by means of various filters**
    
    Attributes:
       
            method: the method choice for baseline correction
            
            params: dictionary of parameter arguments for baselinecorrection 
                                                         
    """    

    def __init__(self, method='', params='', rtrange=''):
        super(type(self), self).__init__()
        self.description = 'Baseline correction'
        self.method = method
        if method=='tophat':
            framelen= np.ceil(params['frame']/rtrange[1])
            framelen = (np.floor(framelen/2))*2 + 1
            params['frame'] = framelen
            self.__se = np.ones((int(framelen))).astype(int)
        self.params = params
              
    def fit(self,ics):       

        """
        Performs baseline correction of generated intensity matrix from GC-MS data by means of various filters
        
        Args:
        
            ics: ion chromatograms for m/z channels 
                
            method: the method choice for smoothing
            
            params: dictionary of parameter arguments for smoothing             
        """  
       
        if self.method=='tophat':
            nsp, nmz = ics.shape
            for i in range(nmz):
                ics[:,i] = ndimage.white_tophat(ics[:,i] , None, self.__se)
            ics[ics<=0] = 0
        return ics

    def export(self,rtrange):
        if self.method=='tophat':
            del self.__se
            self.params['frame'] = self.params['frame']*rtrange[1] 
        
    
if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, NoiseFilter_options);
    settings.description='Noise Filtering';
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
   
    do_noisefilter(settings.parameters['dbfilename'],\
                     smoothmethod = settings.parameters['smoothmethod'], \
                     smoothparams = settings.parameters['smoothparams'],\
                     baselinemethod = settings.parameters['baselinemethod'],\
                     baselineparams = settings.parameters['baselineparams'],\
                     params = settings.parameters['params'])
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();
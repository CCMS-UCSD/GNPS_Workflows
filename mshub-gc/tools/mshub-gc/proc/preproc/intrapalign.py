#!/usr/bin/env python2
"""
*********************************************************************************************
Intra/inter-sample mass drift correction module for chromatography - mass spectrometry data
*********************************************************************************************

The module is designed to adjust for the inherent variation in instrumental 
measurements of moelcular m/z ratios between scans (i.e. within sample)

run python.exe intrapalign.py --help to get info about parameters of the script
 
"""

#===========================Import section=================================

#Importing standard and external modules
import os
import sys;
import h5py
import numpy as np
import time
import traceback
from scipy.interpolate import interp1d

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
import proc.io.manageh5db as mh5

from proc.procconfig import IntraPAlign_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.timing import tic, toc
from proc.utils.printlog import printlog, start_log, stop_log
from proc.preproc.peakdetect import PeakFinder, median_threshold

#==========================================================================
#From here the main code starts


def do_mzalignment(dbfilepath, method='bining', params = {'binshift': 0.3, 'binsize':1, 
                                                          'units': 'Da', 'h5writepath':'/proc'}, istrain = 1):
    """
    Performs intra-sample correction of molecular m/z drifts  between scans of individual samples
    
    Args:
    
        dbfilepath: a user-specified path to the h5 database file
                    
        method: the method choice for intra-sample m/z drift corrections (e.g. bining by default)  
        
        params: dictionary of parameter arguments for the correction method (e.g. ``{'binshift': 0.3, 'binsize':1, 'units': 'Da'})`` for bining) 
             
        dbfilepath: processed intensitiy matrices  
    """     
    
    dataset_names = mh5.get_dataset_names(dbfilepath,dataset_names=[],pathinh5 = '/raw')
    if not dataset_names:
        return
    else:
        params['h5writepath'] = h5Base.correct_h5path(params['h5writepath'])
    
    if istrain==1:
        
        with h5py.File(dbfilepath, 'r') as h5file:
            cmzrange = mh5.load_dataset(h5file,'/raw/cmzrange')
            crtrange = mh5.load_dataset(h5file,'/raw/crtrange')
        
        
        #delete unnecessary variables and save into hdf5 database file
        if method =='binning':
            mzAlignObj = Binmz(method, params, cmzrange, crtrange)
        mzAlignObj.save_procobj(dbfilepath, params['h5writepath'])
        
    elif istrain==0:
        mzAlignObj = Binmz()
        mzAlignObj.load_procobj(dbfilepath, params['h5writepath'])
        
    mzAlignObj.bin_h5(dbfilepath, dataset_names)
        
            
class Binmz(h5Base):
    """
    **The container containing the choice of methods and parameters for intensity matrix generation from GC-MS data
    by means of bining**
    
    Attributes:
       
            params: the list of bining parameters such as bin size and boundary shifts
            
            mzrange: the range of m/z values across all samples
            
            rtrange: the range of retention time values across all samples                                                      
    """    
    
    def __init__(self,method = '', params = '', mzrange = '', rtrange = ''):
        """
        Class parameter initialization
        """
        super(type(self), self).__init__()
        self.description = 'm/z drift correction'  
        self.params = params  
        self.method = method
        self.istrain = 1
        if method=='binning':
            binsize  = params['binsize']  
            binshift = params['binshift']  
            self.mzrange  = mzrange
            self.rtrange  = rtrange    
            self.__binvals = np.arange(mzrange[0]-binshift,mzrange[1]+binshift+binsize,binsize)    
            self.__binids  = self.__binvals[np.arange(0,len(self.__binvals)-1,1)]+0.5*(np.diff(self.__binvals))    
            self.__nbins   = len(self.__binids)    
            self.__rtvals  = np.arange(rtrange[0],rtrange[2],rtrange[1])    
            self.__nrtvals = len(self.__rtvals)
   
    
    def bin_sp(self,mz,sp,scanidx,rt):       
        """
        Performs bining of GC-MS data to generate data intensity matrix [number of mz features x number of scans]
        common across all samples
        
        Args:
        
            dbfilepath: a user-specified path to the h5 database file
                   
            method: the method choice for intra-sample m/z drift corrections (e.g. bining by default)  
            
            params: dictionary of parameter arguments for the correction method (e.g. ``{'binshift': 0.3, 'binsize':1, 'units': 'Da'})`` for bining) 
                     
            dbfilepath: processed intensitiy matrices  
                 
        """     
        # very efficient bining of intensities avoiding any unnecessary loops
        m,nscans = scanidx.shape
        tempsp2D     = np.zeros(( nscans,self.__nbins))
        for i in range(nscans):     
            imz = mz[np.arange(scanidx[0,i],scanidx[1,i]+1,1)]         
            isp = sp[np.arange(scanidx[0,i],scanidx[1,i]+1,1)]         
            tempsp2D[i,:] = np.histogram(imz,self.__binvals,weights=isp)[0]
            
        # also make sure that retention time is the same across all samples
        sp2D     = np.zeros((self.__nrtvals ,self.__nbins))    
        for j in range(self.__nbins):
            jmodel = interp1d(rt,tempsp2D[:,j],kind='linear')
            vals   = jmodel(self.__rtvals[(self.__rtvals>=np.min(rt)) & (self.__rtvals<=np.max(rt))])
            sp2D[(self.__rtvals>=np.min(rt)) & (self.__rtvals<=np.max(rt)),j] = vals
            
        return sp2D,self.__binids,self.__rtvals 

    def bin_h5(self,dbfilepath,datasets):
        """
        Performs bining of GC-MS data to generate data intensity matrix [number of mz features x number of scans]
        common across all samples
        """
        
        with h5py.File(dbfilepath, 'a') as h5file:
        
            printlog("\nPreparing for intra-sample m/z correction %s datasets from %s...\n" % (len(datasets),dbfilepath))
            dataindex  = 0
            i          = 0
            
            peak_width = 0.0;
            dataset_count = 0;
    
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'cmz',data=self.__binids,compression_opts = 5)
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'crt',data=self.__rtvals,compression_opts = 5)
            peak_finder     = PeakFinder(dbfilepath,self.params['h5writepath'],'')
            
            for datasetid in datasets:
                dataindex = dataindex + 1       
                try:
                    mzraw   = mh5.load_dataset(h5file, '/raw' + datasetid + '/mz')
                    spraw   = mh5.load_dataset(h5file, '/raw' + datasetid + '/sp') 
                    scanidx = mh5.load_dataset(h5file, '/raw' + datasetid + '/scan')  
                    rtraw   = mh5.load_dataset(h5file, '/raw' + datasetid + '/time')            
                    sp2D, cmz, crt    = self.bin_sp(mzraw,spraw,scanidx,rtraw)
                    mh5.save_dataset(h5file, self.params['h5writepath'][:-1] + datasetid + '/sp', data=sp2D,
                                     compression_opts = 5)
                    dataset_count += 1;
                    peaks, npeaks = peak_finder.findpeaks_sp(np.sum(sp2D, axis = 1).flatten(), gap = 5)
                    
                    if npeaks > 10:

                        threshold = median_threshold(peaks[0, :])
        
                        mask = peaks[0, :] >= threshold;
        
                        ipeak_widths = peaks[10, mask];
                        
                        if len(ipeak_widths) > 1:
        
                            sorted_peakwidths = ipeak_widths[np.argsort(peaks[0, mask])];
                            
                            slice_count = int(sorted_peakwidths.shape[0]/10);
                            #print(slice_count)
                            if slice_count > 0:
                                quant = np.min(sorted_peakwidths[0:slice_count])
                            else:
                                quant = 0.0;
                            #print(quant)
                            med = np.median(ipeak_widths)/3.0;
                            #print(med)
                            
                            peak_width   += max(med, quant);
                            
                            i = i + 1
                        else:
                            printlog('No peaks passed threshold in %s. Skipping mean peak width estimation...'%datasetid);
                        
                    else:
                        printlog('Less than 10 peaks detected in %s. Skipping mean peak width estimation...'%datasetid);
                    
                    printlog('%s. %s: Successfully corrected and deposited -> %s%s' %(dataindex, datasetid, os.path.basename(dbfilepath),self.params['h5writepath'] ))            

                    target_gname = self.params['h5writepath'][:-1] + datasetid;
                    source_gname = '/raw' + datasetid;
    
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
                    printlog('%s. %s: Failed to be corrected' %(dataindex, datasetid))                    
                    printlog(inst)
                    traceback.print_exc()
                 
            peak_width = peak_width / i 
            
            sizesp = np.array([len(crt),len(cmz), dataset_count])
            
            printlog('Estimated min rt peak width: %s sec or %.2f min'%(peak_width, peak_width / 60.0));
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'peak_width',data = peak_width)
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'mzrange'   ,data = self.mzrange)
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'rtrange'   ,data = self.rtrange) 
            mh5.save_dataset(h5file, self.params['h5writepath'] + 'sizesp'    ,data = sizesp)
    
        
# 
#==============================================================================
     
if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, IntraPAlign_options);
    settings.description='Intra-Sample Peak Alignment';
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
    #settings.parameters['dbfile'] = '/Users/kv/desktop/test/imported_data__1823_22_03_2017.h5'

    do_mzalignment(settings.parameters['dbfilename'],\
                 method = settings.parameters['method'], \
                 params = settings.parameters['params'])
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();
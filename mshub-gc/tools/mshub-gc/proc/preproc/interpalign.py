#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
******************************************************************************
Inter-sample peak alignment module for chromatography - mass spectrometry data
******************************************************************************

The module is designed to adjust for chromatographic peak position variations 
at full profile resolution

run python.exe interpalign.py --help to get info about parameters of the script
 
"""

#===========================Import section=================================

#Importing standard and external modules
import os
import sys;
import h5py
import numpy as np
import traceback;
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

from proc.procconfig import ProfAlign_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.typechecker import is_string, is_number
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts


def do_profile_alignment(dbfilepath, method='rspa', params = {'recursion':1, 
                                                              'minsegwidth':100, 
                                                              'maxpeakshift':10,
                                                              'reference':'mean',
                                                              'h5readpath': '/proc',
                                                              'h5writepath': '/proc'},
                                                                istrain=1):
    """
    Performs advanced adjustment for chromatographic peak position variations at full profile resolution
    using recursive segment-wise peak alignment strategy
    
    Args:
    
        dbfilepath: The database file path
                    
        method: The choice of peak alignment method. Default value: 'rspa', i.e. Recursive segment-wise peak alignment.  
        
        params: The dictionary of peak alignment parameters
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

    if str(params['minsegwidth']).lower() == 'auto':
        params['minsegwidth'] = peak_width * 10.0;
        printlog('Parameter "minsegwidth" is set to %s'%params['minsegwidth']);
    else:
        try:
            params['minsegwidth'] = float(params['minsegwidth'])
        except:
            raise LoggingValueError('Error! %s value for parameter "minsegwidth" cannot be converted to float!'%params['minsegwidth'])
            

    
    if str(params['maxpeakshift']).lower() == 'auto':
        params['maxpeakshift'] = peak_width * 5;
        printlog('Parameter "maxpeakshift" is set to %s'%params['maxpeakshift']);
    else:
        try:
            params['maxpeakshift'] = float(params['maxpeakshift'])
        except:
            raise LoggingValueError('Error! %s value for parameter "maxpeakshift" cannot be converted to float!'%params['maxpeakshift'])
        



    if istrain==1:
        rtrange = mh5.load_dataset(dbfilepath, params['h5readpath'] + 'rtrange') 
        if method=='rspa':
            rtAlObj = RSPA(method,params,rtrange)
            
    elif istrain==0:
            rtAlObj = RSPA()
            rtAlObj.load_procobj(dbfilepath,params['h5readpath'])
        
    rtAlObj.aling_h5(dbfilepath, dataset_names, params['h5readpath'] , params['h5writepath'])
    
    if istrain==1:
         #save into hdf5 database file
        rtAlObj.export()
        rtAlObj.save_procobj(dbfilepath,params['h5writepath'])    
        rtAlObj.save_proc_meta(dbfilepath,params['h5writepath'],params['h5readpath'])
                    
    return
            
class RSPA(h5Base):
   
    """
    **The container containing the choice of profile alignment using recursive segment-wise peak alignment strategy**
    
    Attributes:
       
            'minsegwidth': The minimum segment width for recursion termination, i.e. the width of the widest peak (in seconds)
            
            'maxpeakshift': The maximum allowed peak shift (in seconds)
            
            'recursion': Refines positions of peaks in a recursive fashion if sets to True
            
            'reference': The reference profile with respect to wich all other profiles are to be aligned
    """   
    
    def __init__(self, method ='', params ='', rtrange = ''):
        
        """
        Class parameter initialization
        """
        super(type(self), self).__init__()
        self.description  = 'Retention time drift correction'
        if method=='rspa':
            self.minsegwidth  = np.ceil(params['minsegwidth']/rtrange[1])
            self.maxpeakshift = np.ceil(params['maxpeakshift']/rtrange[1])
            self.recursion    = params['recursion']
            self.reference    = params['reference']
            self.rtrange      = rtrange 
            self.ref2D        = []

    def aling_h5(self,dbfilepath,datasets,h5readpath,h5writepath):
        
        if not self.ref2D:
            self.get_refsp_h5(dbfilepath,datasets,h5readpath)
            
        printlog("\nPerforming inter-sample retention time profile alignment across %s datasets from \n%s...\n" % (len(datasets),dbfilepath))
        dataindex = 0 
        with h5py.File(dbfilepath, 'a') as h5file:   
        
            mh5.save_dataset(h5file, h5writepath + '/ref2D', data = self.ref2D, compression_opts = 5)
            
            for datasetid in datasets:
                dataindex = dataindex + 1                
                try:
                    sp2D = mh5.load_dataset(h5file, h5readpath[:-1] + datasetid+ '/sp')
              
                    nrt, nmz = sp2D.shape
                    for i in range(nmz):
                        alprof = self.align(sp2D[:,i],self.ref2D[:,i])
                        sp2D[:,i] =alprof
                        
                    mh5.save_dataset(h5file,h5writepath[:-1] + datasetid+ '/sp',data=sp2D,compression_opts = 5)
                    
                    printlog('%s. %s: Successfully aligned and deposited -> %s%s' %(dataindex, datasetid, os.path.basename(dbfilepath),h5writepath))
                    
                    
                    target_gname = h5writepath[:-1] + datasetid;
                    source_gname = h5readpath[:-1] + datasetid;
        
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
                    printlog('%s. %s: Failed to be deposited' %(dataindex, datasetid))  
                    printlog(inst)
                    traceback.print_exc()
                    
                    
        
        
        
    def get_refsp_h5(self,dbfilepath,datasets,h5readpath):
        
        with h5py.File(dbfilepath, 'r') as h5file:    
            i = 0
            printlog("\nPreparing reference profile for inter-sample retention time drift alignment across %s datasets from \n%s...\n" % (len(datasets),dbfilepath))
            dataindex = 0 
            for datasetid in datasets:
                dataindex = dataindex + 1        
                try:        
                    sp2D = mh5.load_dataset(h5file,h5readpath[:-1] + datasetid+ '/sp')
                    if i==0:
                        i = i + 1
                        ref2D = sp2D
                        continue
                    if self.reference=='mean':
                        ref2D = (sp2D + ref2D)                  
                    i = i + 1
                    printlog('%s. %s: Successfully updated from -> %s%s' %(dataindex, datasetid, os.path.basename(dbfilepath),h5readpath))
                except Exception as inst:
                    printlog('%s. %s: Failed' %(dataindex, datasetid))  
                    printlog(inst)
                    traceback.print_exc()
            
            if self.reference=='mean':
                self.ref2D = ref2D/i
                
        
        
         
    def align(self,test,ref):
        """
        Performs peak pair-wise peak alignment of the test profile againts the reference profile using the RSPA algorithm
        
        Args:
        
            test: The test profile
                   
            ref: The reference profile
            
        Returns:
            
            alignedtest: The aligned test prifle                
        """     
        if np.var(test)==0 or np.var(ref)==0:
            alignedtest=test
            return alignedtest
        
        if self.recursion==1:
            alignedtest = test
            if len(test)<=self.minsegwidth:
                return alignedtest
            shift = self.__fftcov(test,ref)
            if np.abs(shift)<len(test):
                alignedtemp = self.__do_seg_shift(test,shift)
                if np.var(alignedtemp)<=0.0001:
                    return alignedtest 
                alignedtest = alignedtemp
            else:
                return alignedtest
            
            divpoint = self.__get_div_point(alignedtest,ref)
            
            if not is_number(divpoint):
                return alignedtest
            
            testleft  = alignedtest[np.arange(0,divpoint,1)]
            refleft   = ref[np.arange(0,divpoint,1)]
            testright = alignedtest[np.arange(divpoint,len(ref),1)]
            refright  = ref[np.arange(divpoint,len(ref),1)]
            
            alignedtestleft  = self.align(testleft,refleft);
            alignedtestright = self.align(testright,refright);
            
            alignedtest   = np.hstack([alignedtestleft, alignedtestright]);
        
        else:
            shift = self.__fftcov(test,ref)
            alignedtest=test
            if np.abs(shift)<len(test):
                alignedtemp = self.__do_seg_shift(test,shift)
                if np.var(alignedtemp)<=0.0001:
                    return alignedtest
                alignedtest = alignedtemp
                
        return alignedtest
    
    def __fftcov(self,test,ref):
        """
        Performs fast fourier transform-based convolution for peak shift estimation
        between test and reference profiles
        
        Args:
        
            test: The test profile
                   
            ref: The reference profile
            
        Returns:
            
            shift: The estimated positional shift of the test profile againts its reference               
        """     
        seglen = len(test)
        seglen = 2 ** int(np.ceil(np.log2(seglen)))
        maxpeakshift = self.maxpeakshift
        if seglen < maxpeakshift:
            maxpeakshift = seglen;
             
        X = np.fft.rfft(test, seglen)
        Y = np.fft.rfft(ref, seglen)
        covtestref = np.fft.irfft(Y * np.conj(X))
        if maxpeakshift>int(seglen/2):
            covindcs = np.arange(0,seglen,1)
        else:
            covindcs = np.hstack((np.arange(0,maxpeakshift+1,1), np.arange(seglen-maxpeakshift-1,seglen,1)))
        covindcs = covindcs.astype(int)
        
        maxpos = np.argmax(covtestref[(covindcs)])
        maxpos = covindcs[maxpos]
        if maxpos>int(seglen/2):
            shift = int(maxpos-seglen)
        else:
            shift = int(maxpos)
            
        return shift
    
    def __do_seg_shift(self,test,shift):
        """
        Performs shifting of the test profile to align to its reference
        
        Args:
        
            test: The test profile
                   
            ref: The reference profile
            
        Returns:
            
            alignedtest: The aligned test profile
        """
         
        if shift>0:
            alignedtest = np.hstack([test[0]*np.ones((shift+1)),test[1:len(test)-shift]])
        elif shift<0:
            alignedtest = np.hstack([test[-shift:],np.ones((-shift))*test[-1]])
        else:
            alignedtest = test 
        return alignedtest
    
    def __get_div_point(self,test,ref):
       
        """
        Identifies the position to divide the test and reference profiles for recusrive alignment  
        
        Args:
        
            test: The test profile
                   
            ref: The reference profile
            
        Returns:
            
            divpoint: The position to divide test and reference profiles/segments
        """
        
        seglen = len(test)
        M        = np.ceil(seglen/2);
        midcnst  = np.floor(M/2);
        mididx   = np.arange(M-midcnst,M+midcnst,1).astype(int)
        test     = test[mididx]
        ref      = ref[mididx]
        
        idx = np.argmin(test*ref)
        divpoint = mididx[idx]+1

        return divpoint    
    
    def export(self):
        """
        Prepares peak alignment parameter set for export  
        """
        self.minsegwidth = self.minsegwidth*self.rtrange[1]
        self.maxpeakshift = self.maxpeakshift*self.rtrange[1]

    
if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, ProfAlign_options);
    settings.description='Profile Alignment';
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
   
    do_profile_alignment(settings.parameters['dbfilename'],\
                     method = settings.parameters['method'], \
                     params = settings.parameters['params'])
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();
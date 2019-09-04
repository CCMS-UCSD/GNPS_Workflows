# -*- coding: utf-8 -*-
"""
*******************************************************************
Peak detection module for chromatography - mass spectrometry data
*******************************************************************

The module is designed to identify and integrate chromatographic peaks from
generated chromatography - mass spectrometry data matrix

run python.exe peakdetect.py --help to get info about parameters of the script
 
"""
#===========================Import section=================================

#Importing standard and external modules
import os
import h5py
import numpy as np
import traceback
import sys;
import time;
from scipy import sparse 

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

from proc.procconfig import PeakDetection_options
from proc.utils.cmdline import OptionsHolder
from proc.utils.signalproc import get_threshold;
from proc.utils.timing import tic, toc;
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.h5utils import h5write_strings
from sklearn.decomposition import NMF
from proc.utils.printlog import printlog, start_log, stop_log, LoggingException

#==========================================================================
#From here the main code starts

def do_peak_detection(parameters):
    
    """ 
    Performs peak detection, filtering and fragment pattern exctraction on data intensity matrix 
                                                                    [retention times x m/z ratios]
    
    Args:
    
        method: the choice of peak detection method. 
                    
        params: the dictionary of peak detection parameters {param1: value1, param2: value2}

        rtvals: a vector of retention times
        
        mzvals: a vector of m/z ratios                                      
    """   
    
    dbfilepath = parameters['dbfilename'];
    
    peak_detect_method = parameters['peak_detect_method'];    
    peak_detect_params = parameters['peak_detect_params'];
    
    peak_filter_method = parameters['peak_filter_method'];    
    peak_filter_params = parameters['peak_filter_params'];
    
    peak_group_method = parameters['peak_group_method'];    
    peak_group_params = parameters['peak_group_params'];
    
   
    istrain = 1    
    
    parameters['h5readpath']  = h5Base.correct_h5path(parameters['h5readpath'])
    parameters['h5writepath'] = h5Base.correct_h5path(parameters['h5writepath'])
    dataset_names = mh5.get_dataset_names(dbfilepath,dataset_names=[],\
                                          pathinh5 = parameters['h5readpath'][:-1])
    if not dataset_names:
        return
        
    peak_width = mh5.load_dataset(dbfilepath, parameters['h5readpath'] + 'peak_width');
    printlog('Loaded min estimated peak width: %s seconds'%peak_width);
    mh5.save_dataset(dbfilepath, parameters['h5writepath'] + 'peak_width',\
                                 data=peak_width)
    
    
    
    if str(peak_detect_params['min_width']).lower() == 'auto':
        peak_detect_params['min_width'] = peak_width * 0.3;
        printlog('Parameter "min_width" is set to %s'%peak_detect_params['min_width']);
    else:
        try:
            peak_detect_params['min_width'] = float(peak_detect_params['min_width'])
        except:
            #printlog('Error! %s value for parameter "min_width" cannot be converted to float!'%peak_detect_params['min_width']);
            raise LoggingValueError('Error! %s value for parameter "min_width" cannot be converted to float!'%peak_detect_params['min_width']);


    if istrain==1:
        peak_finder = PeakFinder(dbfilepath, parameters['h5readpath'], parameters['h5writepath'], peak_detect_method, peak_detect_params, istrain)
        peak_filter = PeakFilter(dbfilepath, parameters['h5readpath'], parameters['h5writepath'],  peak_filter_method,  peak_filter_params, istrain)
        peak_grouper = PeakCluster(dbfilepath, parameters['h5readpath'], parameters['h5writepath'], peak_group_method, peak_group_params, istrain) 
            
    elif istrain==0:
        peak_finder = PeakFinder(dbfilepath, parameters['h5readpath'], parameters['h5writepath'])
        peak_finder.load_procobj(dbfilepath, parameters['h5writepath'])  
       
        peak_filter = PeakFilter(dbfilepath, parameters['h5readpath'], parameters['h5writepath']);
        peak_filter.load_procobj(dbfilepath, parameters['h5writepath'])
 
        peak_grouper = PeakCluster(dbfilepath, parameters['h5readpath'], parameters['h5writepath']);
        peak_grouper.load_procobj(dbfilepath, parameters['h5writepath'])
        
    # detect peaks
    procdataset_names = peak_finder.findpeaks_h5(dataset_names)
    
    # filter peaks
    peak_filter.filter_peaks(procdataset_names);
    
    # group peaks
    peak_grouper.process_peaks(procdataset_names);
    
    # Finalize processing and copy over metadata
    
    finalize_metadata(dbfilepath, parameters['h5readpath'], parameters['h5writepath'], procdataset_names);
    
    if istrain==1:
        #save into hdf5 database file
        peak_finder.save_procobj(dbfilepath, parameters['h5writepath'])  
        peak_filter.save_procobj(dbfilepath, parameters['h5writepath'])
        peak_grouper.save_procobj(dbfilepath, parameters['h5writepath'])        
    
    #printlog(parameters['h5readpath'][:-1])
    #printlog(dataset_names)
               
    return
     

class PeakFinder(h5Base):
   
   """   
   ** The class containing the choice of methods and parameters for fast peak detection from one dimensional signals**
    
   Attributes:
       
        method: the choice of peak detection method. 
                    
        params: the dictionary of peak detection parameters {param1: value1, param2: value2}

        rtvals: a vector of retention times
        
        mzvals: a vector of m/z ratios 
   """    
    
   def __init__(self, dbfilepath, h5readpath, h5writepath, method = '', params = '', istrain = 0):     
       super(type(self), self).__init__()
       self.description = 'Peak finder'     
       self.method = method     
       self.params = params
       self.dbfilepath = dbfilepath
       self.h5readpath = h5readpath
       self.h5writepath = h5writepath
       self.istrain = istrain
       self.__rtvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'crt')     
       self.__mzvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'cmz')
  
       if 'min_width' in self.params:
           self.params['min_width'] = int(self.params['min_width']/( self.__rtvals[2]- self.__rtvals[1])) 
                     
   def findpeaks_h5(self, datasets):            
        
        """
        Performs peak detection of generated intensity matrix from spectral data by means of various algorithms
        
        Args:
        
            dbfilepath: database file path and name
                
            datasets: datasets for peak detection
              
        """  
        i=0   
        printlog('\n' + "Preparing for feature detection " + os.path.basename(self.dbfilepath)+'\n')
              
        dataindex= 0
        procdataset_names = []

        with h5py.File(self.dbfilepath, 'a') as h5file:

            for datasetid in datasets:     
                dataindex = dataindex + 1
                try:    
                    sp2D = mh5.load_dataset(h5file, self.h5readpath + datasetid + '/sp')        
                    if self.method=='smoothderiv':        
                            peaks = self.findpeaks_ics(sp2D)                
        
                            if self.params['local_baseline_correction'] != 'no':
                                printlog('Correcting local baseline...');
                                peaks = self.correct_local_baseline(peaks);
                                
                            mh5.save_dataset(h5file,self.h5writepath + datasetid + '/sp_unfiltered_peaks',\
                                             data = peaks, compression_opts = 5)
        
                    printlog('%s. %s: Successfully detected and deposited -> %s %s' \
                              %(dataindex, datasetid, os.path.basename(self.dbfilepath),\
                                self.h5writepath + datasetid + '/sp_unfiltered_peaks')) 
                    procdataset_names.append(datasetid)
                    i = i + 1
                except Exception as inst:
                    printlog('%s. %s: Failed' %(dataindex, datasetid))  
                    printlog(inst)
                    traceback.print_exc()
                #    pass
            
            if 'min_width' in self.params:
               self.params['min_width'] = self.params['min_width']*( self.__rtvals[2]- self.__rtvals[1]) 
              
        return procdataset_names

   def correct_local_baseline(self, peaks):
        if peaks.shape[1]>0:
             peaks[5,:] = np.subtract(np.subtract(
                             peaks[5,:],
                             np.multiply(
                                 np.divide(
                                         np.subtract(peaks[6,:], peaks[4,:]), 
                                         peaks[10,:]),
                                 np.subtract(peaks[2,:], peaks[1,:]))
                             ), peaks[4,:]);  #linear interpolate and correct for zero
             
             peaks[0,:] = np.subtract(peaks[0,:],
             
                             np.multiply(np.add(peaks[6,:], peaks[4, :])*0.5,
                                         peaks[10,:])
                         ) # subtract baseline from integral
             
             peaks[6,:] = 0.0;
             peaks[4,:] = 0.0;
             peaks = peaks[:, peaks[5,:]>0.0]; #remove negative and zero peaks
             peaks = peaks[:, peaks[0,:]>0.0]; #remove negative and zero integrals
        return peaks
              
   def findpeaks_ics(self,ics):            
        
        """
        Performs peak detection of generated intensity matrix from spectral data by means of various algorithms
        
        Args:
        
            ics: ion chromatograms for m/z channels 
                
            method: the method choice for smoothing
            
            params: dictionary of parameter arguments for smoothing 
            
        """  
        
        if self.method=='smoothderiv':
            nsp,nmz = ics.shape          
            peak_params = np.array([[]]*13)                     
            for i in range(nmz):         
                ipeak_params,npeaks = self.findpeaks_sp(ics[:,i], self.params['min_width'])             
                if npeaks >0:                 
                    mzindex     = i *np.ones([1,npeaks])                 
                    ipeak_params = np.vstack([ipeak_params,
                                              self.__mzvals[mzindex.astype(int)], #11 mz value
                                              mzindex.astype(int) #12 mz index
                                              ])             
                    peak_params = np.hstack([peak_params, ipeak_params])                                     
                    
        return peak_params
      
   def findpeaks_sp(self,sp,gap):    
        
        """
        Returns a matrix of peak positions, values and integrals of detected peaks
        
        peakparams = np.vstack([peakint, # 0, RT integral
                                        self.__rtvals[peakvalleys[0,:]], #1, RT start
                                        self.__rtvals[peakmaxindcs], #2, RT peak
                                        self.__rtvals[peakvalleys[1,:]], #3, RT end
                                        sp[peakvalleys[0,:]],  #4  Peak start height
                                        sp[peakmaxindcs], #5, peak top height
                                        sp[peakvalleys[1,:]], #6, peak end height
                                        peakvalleys[0,:], #7, peak start index 
                                        peakmaxindcs, #8, peak top index
                                        peakvalleys[1,:], #9, peak end index
                                        self.__rtvals[peakvalleys[1,:]]-self.__rtvals[peakvalleys[0,:]], #10, peak width
                                        ])  
            
        Args:
            
                sp: input signal vector (e.g. spectral or chromatographic data)
                    
                gap: the minimum gap between peaks (in data points)
                
                int_thr: intensity threshold (the data are assumed to be smoothed)
        
        Returns:
                
                peakparams: a vector of the local peak maxima indices
        """      
       
        if sum(sp)==0:          
            peakparams = np.array([[]]*10)     #????????    
            npeaks = 0           
            return peakparams,npeaks 
        
        try:
            # detect accurately peak maximum positions
            peakmaxindcs = self.findpeakmaxs(sp,gap=gap)           
            # detect accurately peak minimum positions
            peakminindcs = self.findpeakmins(sp,gap=gap)           
            # remove peak maxima outside the range of peak staring and ending positions
            peakmaxindcs = peakmaxindcs[peakmaxindcs>min(peakminindcs)]
            peakmaxindcs = peakmaxindcs[peakmaxindcs<max(peakminindcs)]           
            # project peak max positions between peak adjacent minima
            idx,peakminidx = np.histogram(peakmaxindcs,peakminindcs)           
             # exctract cumulative integral values
            isp = self.__cumtrapez(self.__rtvals,sp)           
            # now calculate peak integrals 
            peakint = isp[peakminidx[1:]] - isp[peakminidx[:-1]]           
            # now remove noisy peaks
            peakvalleys = np.vstack([peakminidx[:-1].astype(int),peakminidx[1:].astype(int)])
                    
            # find region specific corresponding peak maxima
            if max(idx)>1:               
                regions  = np.where(idx>1)[0]               
                delindcs = np.array([])               
                for i in regions:            
                    indcs    = peakmaxindcs[(peakmaxindcs>peakvalleys[0,i]) & (peakmaxindcs<peakvalleys[1,i])]                   
                    isp      = sp[indcs]+np.random.random(len(sp[indcs]))/100                   
                    delindcs = np.hstack([delindcs,indcs[isp!=max(isp)]])               
                # delete redundant peaks
                peakmaxindcs = np.setdiff1d(peakmaxindcs,delindcs.astype(int))
                
            # Simple criteria to detect noisy or real peaks (not yet thresholding)
            # remove peak regions without peak maxima
            peakvalleys = peakvalleys[:,idx>0]
            peakint     = peakint[idx>0]
            
            # remove peaks with the baseline values being larger than the peak maxima values 
            peakindcs = np.logical_and(sp[peakvalleys[0,:]]<sp[peakmaxindcs],\
                                       sp[peakvalleys[1,:]]<sp[peakmaxindcs])
            peakvalleys  = peakvalleys[:,peakindcs]
            peakint      = peakint[peakindcs]
            peakmaxindcs = peakmaxindcs[peakindcs]
            
            # remove peak regions with the width smaller than the width of the smallest peak or gap between peaks
            peakindcs    = peakvalleys[1,:]-peakvalleys[0,:] > gap
            peakvalleys  = peakvalleys[:,peakindcs]
            peakint      = peakint[peakindcs]
            peakmaxindcs = peakmaxindcs[peakindcs]
            
            # basic check
            n,npeaks     = peakvalleys.shape
            if npeaks==len(peakmaxindcs): 
                peakparams = np.vstack([peakint, # 0, Peak integral
                                        self.__rtvals[peakvalleys[0,:]], #1, RT start
                                        self.__rtvals[peakmaxindcs], #2, RT peak
                                        self.__rtvals[peakvalleys[1,:]], #3, RT end
                                        sp[peakvalleys[0,:]],  #4  Peak start height
                                        sp[peakmaxindcs], #5, peak top height
                                        sp[peakvalleys[1,:]], #6, peak end height
                                        peakvalleys[0,:], #7, peak start index 
                                        peakmaxindcs, #8, peak top index
                                        peakvalleys[1,:], #9, peak end index
                                        self.__rtvals[peakvalleys[1,:]]-self.__rtvals[peakvalleys[0,:]], #10, peak width
                                        ])  
            else: 
                printlog('Peak detection error: not all peaks were correctly detected ')
        except Exception as inst:
            printlog(inst)
            traceback.print_exc()
            peakparams = np.array([[]]*10)  
            npeaks = 0
       
        return peakparams,npeaks
   
   def findpeakmaxs(self,sp, gap=3, int_thr = None):
        
        """
        Returns a vector of the local peak maxima (peaks) of the input signal vector
        
        Args:
            
                sp: input signal vector (e.g. spectral or chromatographic data)
                    
                gap: the minimum gap between peaks (in data points)
                
                int_thr: intensity threshold (the data are assumed to be smoothed)
        
        Returns:
                
                peakindcs: a vector of the local peak maxima indices
        """      
        # number of data points
        ndp = len(sp)      
        x = np.zeros(ndp+2*gap)      
        x[:gap] = sp[0]-1.e-6      
        x[-gap:] = sp[-1]-1.e-6      
        x[gap:gap+ndp] = sp      
        peak_candidate = np.zeros(ndp)      
        peak_candidate[:] = True
        
        for s in range(gap):      
            # staring
            start = gap - s - 1
            h_s = x[start : start + ndp]            
            # central
            central = gap
            h_c = x[central : central + ndp]            
            # ending
            end = gap + s + 1
            h_e = x[end : end + ndp]            
            peak_candidate = np.logical_and(peak_candidate, np.logical_and(h_c > h_s, h_c > h_e))
    
        peakindcs = np.argwhere(peak_candidate).flatten()              
        if int_thr is not None:
            peakindcs = peakindcs[sp[peakindcs] > int_thr]
        
        return peakindcs
   
        
   def findpeakmins(self,sp, gap=3, int_thr = None):
        
        """
        Returns a vector of the local peak minima (peaks) of the input signal vector
        
        Args:
            
                sp: input signal vector (e.g. spectral or chromatographic data)
                    
                gap: the minimum gap between peaks (in data points)
                
                int_thr: intensity threshold (the data are assumed to be smoothed)
        
        Returns:
                
                peakindcs: a vector of the local peak maxima indices
        """      
        # number of data points
        ndp = len(sp)
        sp  = -sp
        x = np.zeros(ndp+2*gap)      
        x[:gap] = sp[0]-1.e-6      
        x[-gap:] = sp[-1]-1.e-6      
        x[gap:gap+ndp] = sp      
        peak_candidate = np.zeros(ndp)      
        peak_candidate[:] = True
        
        for s in range(gap):      
            # staring
            start = gap - s - 1
            h_s = x[start : start + ndp]            
            # central
            central = gap
            h_c = x[central : central + ndp]            
            # ending
            end = gap + s + 1
            h_e = x[end : end + ndp]            
            peak_candidate1 = np.logical_and(peak_candidate, np.logical_and(h_c > h_s, h_c > h_e))
            peak_candidate2 = np.logical_and(peak_candidate, np.logical_and(h_c == h_s, h_c > h_e))   
            peak_candidate3 = np.logical_and(peak_candidate, np.logical_and(h_c > h_s, h_c == h_e))
            peak_candidate  = np.logical_or.reduce((peak_candidate1,peak_candidate2,peak_candidate3))  
        
        peakindcs = np.argwhere(peak_candidate).flatten()              
        if int_thr is not None:
            peakindcs = peakindcs[sp[peakindcs] > int_thr]
        
        return peakindcs
        
   def __cumtrapez(self,x,sp):
        
        """
        Returns a vector of cumulative spectral integral intensities
        
        Args:
            
                sp: spectral or chromatographic data
                    
                x: retention time or m/z feature vector
                
                int_thr: intensity threshold (the data are assumed to be smoothed)
        
        Returns:
            
                cumsp: cumulative integral of spectral intensities
        """
        dx = x[1:] - x[:-1] 
        dsp = 0.5*(sp[1:] + sp[:-1])
        cumsp = np.hstack([0,np.cumsum(dx*dsp)])
        
        return cumsp


class PeakFilter(h5Base):
    """   
    ** The class containing the choice of methods and parameters for fast peak filtering**
    
    Attributes:
       
        method: the choice of peak filtering method. 
                    
        params: the dictionary of peak filtering parameters {param1: value1, param2: value2}

        rtvals: a vector of retention times
        
        mzvals: a vector of m/z ratios 
        
    """        
    def __init__(self, dbfilepath, h5readpath, h5writepath, method = '', params = '', istrain = 0):     
        super(type(self), self).__init__()
        self.description = 'Peak filter'     
        self.method = method     
        self.params = params
        self.dbfilepath = dbfilepath
        self.h5readpath = h5readpath
        self.h5writepath = h5writepath
        self.istrain = istrain
  
    def init_thr(self):
        """
        
        Check the validity of the user-input settings for peak filtering 
       
        """
        auto_thr = False
        exempts  = ['global']
        thr      = dict()
        for iparam in self.params.keys():
            if iparam in exempts:
                continue
            else:
                thr[iparam] = []
                if str(self.params[iparam]).lower() == 'auto':
                    auto_thr = np.logical_or(auto_thr,self.params[iparam]=='auto')
                elif str(self.params[iparam]).lower() == 'none':
                    continue
                else:
                    try:
                        thr[iparam] = float(self.params[iparam]);
                    except:
                        raise LoggingValueError('%s threshold should be a number or "auto"! %s submitted instead!'\
                                         %iparam, self.params[iparam]);
                        printlog('Entered Threshold %s'%self.params[iparam])   
        self.thr = thr
        return auto_thr
    
    def append_thr(self,peaks):
        """
        
        Estimate and accumulate sample-specific filtering thresholds
       
        """
        if self.method == 'slope':
            if str(self.params['int_thr']).lower() == 'auto':
                int_thr = self.get_intensity_threshold(peaks)
                self.thr['int_thr'].append(int_thr)
                #pass_filter = peaks[5,:]>int_thr
                #peaks = peaks[:,pass_filter]
            left_ang_thr,right_ang_thr = self.get_slope_values(peaks,isthreshold=1)    
            if str(self.params['left_ang_thr']).lower() == 'auto':
                self.thr['left_ang_thr'].append(left_ang_thr) 
            if str(self.params['right_ang_thr']).lower() == 'auto':
                self.thr['right_ang_thr'].append(right_ang_thr)
        
    def adjust_thr(self):
        """
        
        Calculate the common thresholds for all samples if global parameter sets to "yes"
       
        """
        if self.params['global'] =='yes':
            for i in self.thr.keys():
                self.thr[i] = np.median(np.array(self.thr[i] ).astype(float))
        elif self.params['global'] =='no':
            for i in self.thr.keys():
                self.thr[i] = np.array(self.thr[i] ).astype(float)
    
    def apply_thr(self,peaks,dataindex):
        """
        
        Apply thresholds iteratively for each sample
       
        """
        if self.method == 'slope': 
            pass_filter = np.ones([1,len(peaks[1,:])])==1
            pass_filter = pass_filter.flatten()
            if len(self.thr['int_thr'])>0: 
                pass_filter = np.logical_and(pass_filter,\
                                            peaks[5,:]>self.get_thr(self.thr['int_thr'],dataindex))
            left_angles, right_angles = self.get_slope_values(peaks, isthreshold=0)
            if len(self.thr['left_ang_thr'])>0:
                pass_filter = np.logical_and(pass_filter,\
                                            left_angles>self.get_thr(self.thr['left_ang_thr'],dataindex))
            if len(self.thr['right_ang_thr'])>0:
                pass_filter = np.logical_and(pass_filter,\
                                            right_angles>self.get_thr(self.thr['right_ang_thr'],dataindex))
            return pass_filter
                            
    def get_thr(self,thr_vals,index):
        """
        
        Select appropriate threshold from a vector 
       
        """
        
        index = int(index)
        if len(thr_vals)>1:
            thr_val = thr_vals[index]
        else:
            thr_val = thr_vals[0]
        return thr_val
            
    def filter_peaks(self, procdataset_names):
        """
        Derive and save the mask to filter out remove noisy peaks  
        
        Args: 
            
               
        
        Returns:
            
                cumsp: cumulative integral of spectral intensities
        """
        printlog('\n...Performing filtering of identified peaks...\n')
                            
        with h5py.File(self.dbfilepath, 'a') as h5file:
            
            dataset_count = len(procdataset_names);
            if dataset_count>0:
                
                # check if we need to iterate through samples to estimate thresholds iteratively
                auto_thr = self.init_thr()
                                
                if auto_thr == True:
                    printlog('Estimating sample-specific parameters for automated peak filtering') 
                    dataindex = 0        
                    for datasetid in procdataset_names:     
                        dataindex = dataindex + 1
           
                        peaks = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/sp_unfiltered_peaks')
                        
                        if peaks.shape[1] > 0:
                        
                            self.append_thr(peaks)
                            printlog('%s. %s: Done -> %s%s' \
                                  %(dataindex, datasetid, os.path.basename(self.dbfilepath),\
                                     '/sp_unfiltered_peaks')) 
                        else:
                            printlog('No peaks detected!');
                            
                self.adjust_thr()
                    
                # now apply thresholds
                printlog('\n\nApplying filters...\n');
                dataindex = 0                
                for datasetid in procdataset_names:     
                    dataindex = dataindex + 1
                    
                    peaks = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/sp_unfiltered_peaks')
                    
                    if peaks.shape[1] > 0:
                    
                        pass_filter = self.apply_thr(peaks,dataindex-1)
                        #peaks = peaks[:, pass_filter]
                                
                        mh5.save_dataset(h5file, self.h5writepath + datasetid + '/peaks_pass_filter',\
                                                 data = pass_filter.astype(float), compression_opts = 5)
                            
                        printlog('%s. %s: Before: %s After Filtering: %s Saved to --> %s' \
                                  %(dataindex, datasetid, str(int(len(pass_filter))),str(int(sum(pass_filter))),\
                                  self.h5writepath)) 
                    else:
                        printlog('No peaks detected!');
                
    def get_intensity_threshold(self, peaks):     
      """    
      Calculate intensity threshold
        
      """
        # get intensity threshold      
      threshold = median_threshold(peaks[5,:])
      #printlog('Median Threshold %s'%threshold)
        
      return threshold    
     
    def get_slope_values(self, peaks, isthreshold = 1):
        """
        Calculate slope value to filter out remove noisy peaks  
        
        """
            
        # get slope threshold
        
        #coeff = 3.0/5000
        coeff=1
        left_output = np.arctan(np.divide(np.subtract(peaks[5,:], peaks[4,:])*coeff, 
                  np.subtract(peaks[2,:], peaks[1,:])))/np.pi*180.0;
        
        right_output = np.arctan(np.divide(np.subtract(peaks[5,:], peaks[6,:])*coeff, 
                  np.subtract(peaks[3,:], peaks[2,:])))/np.pi*180.0;
        
        if isthreshold == 1:
            left_output  = get_threshold(left_output);
            right_output = get_threshold(right_output);
            
        return left_output, right_output       


class PeakCluster(h5Base):
    
    def __init__(self, dbfilepath, h5readpath, h5writepath, method = '', params = '', istrain = 0):     
        #super(type(self), self).__init__(dbfilepath,dbfilepath, h5readpath, h5writepath)
        super(type(self), self).__init__()
        self.description = 'Peak Grouper'     
        self.method = method     
        self.params = params
        self.dbfilepath = dbfilepath
        self.h5readpath = h5readpath
        self.h5writepath = h5writepath
        self.istrain = istrain

    def process_peaks(self, procdataset_names):               
        """    
        Performs grouping, fragmention pattern exctraction and integral calculations for chromatographic peaks
        
        """
        # 1: cluster similar/identical chromatographic peaks to a common retention vector/profile
        if self.method =='kernel':
            if self.params['individual'] == 'no':
                self.cluster_rts_kernel(procdataset_names)
            else:
                self.cluster_individual_rts_kernel(procdataset_names)
        
        # 2: exctract fragmentation patterns for each common chromatographic peaks
        if self.params['individual'] == 'no':
            
            if len(procdataset_names)<5:
                printlog('\n The number of samples (%s) is too small for component deconvolution' \
                              %(len(procdataset_names)))
                self.params['frag_pattern']='max'
            
            if self.params['frag_pattern']=='deconvolution':
                self.deconvolve_peaks(procdataset_names)
                printlog('Deconvolution completed in')
                self.intensity_and_rank(procdataset_names)
                return
            else:
                self.extract_fragment_patterns(procdataset_names)
        else:
            self.extract_fragment_patterns_individual(procdataset_names)
            
        # 3: calculate chromatographic peak integrals for each sample data-set
        if self.params['individual'] == 'no':    
            self.get_peak_integrals(procdataset_names)
        else:
            self.get_peak_integrals_individual(procdataset_names)
            
        if self.params['individual'] == 'no':        
            self.intensity_and_rank(procdataset_names);
        else:
            self.intensity_and_rank_individual(procdataset_names);

    def intensity_and_rank(self, procdataset_names):

        printlog('\n ... Intensity and rank calculation ...')

        dataset_count = len(procdataset_names)

        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                if self.h5writepath + '/quantity_integrals' in h5file:

                    q_i = h5file[self.h5writepath + '/quantity_integrals']

                    q = np.array(q_i).flatten();

                    mask = q > 0.0;

                    q_masked = q[mask];                        

                    max_integral = np.max(q_masked);

                    if max_integral <= 0.0:
                        max_integral = 1;
                    
                    order = np.argsort(-q_masked);
                    
                    rev_order = np.zeros(q_masked.shape, dtype = np.int64)
                    rev_order[order] = np.arange(1, q_masked.shape[0] + 1, dtype = np.int64)
                    orderall = np.zeros(q.shape, dtype = np.int64);
                    rel_integral = np.zeros(q.shape, dtype = np.float64)
                    orderall[mask] = rev_order
                    rel_integral[mask] = q_masked / max_integral * 100.0
                    
                    mh5.save_dataset(h5file, self.h5writepath + '/rel_integrals',\
                                             data = rel_integral.reshape(q_i.shape), compression_opts = 5)

                    mh5.save_dataset(h5file, self.h5writepath + '/order',\
                                             data = orderall.reshape(q_i.shape), compression_opts = 5)

                else:
                    printlog('Error! quantity_integrals not found in [%s]%s!'%(self.dbfilepath, self.h5writepath));
                    
    def intensity_and_rank_individual(self, procdataset_names):
        printlog('\n... Intensity and rank calculation ...');

        dataset_count = len(procdataset_names)

        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    printlog(datasetid);
                
                    if self.h5writepath + datasetid + '/quantity_integrals' in h5file:
    
                        q_i = h5file[self.h5writepath + datasetid + '/quantity_integrals']
    
                        q = np.array(q_i).flatten();
    
                        mask = q > 0.0;
    
                        q_masked = q[mask];                        
    
                        max_integral = np.max(q_masked);
    
                        if max_integral <= 0.0:
                            max_integral = 1;
                        
                        order = np.argsort(-q_masked);
                        
                        orderall = np.zeros(q.shape, dtype = np.int64);
                        
                        rel_integral = np.zeros(q.shape, dtype = np.float64);
                        
                        orderall[mask] = order;
                        
                        rel_integral[mask] = q_masked / max_integral * 100.0;
                        
                        mh5.save_dataset(h5file, self.h5writepath + datasetid + '/rel_integrals',\
                                                 data = rel_integral.reshape(q_i.shape), compression_opts = 5)
    
                        mh5.save_dataset(h5file, self.h5writepath + datasetid + '/order',\
                                                 data = orderall.reshape(q_i.shape), compression_opts = 5)
    
                    else:
                        printlog('Error! quantity_integrals not found in [%s]%s!'%(self.dbfilepath, self.h5writepath + datasetid));
                        
    def deconvolve_peaks(self,procdataset_names):
        """    
        Performs deconvolution of spectral data matrix of each chromatographic peak to separate co-eluting components 
        
        """
        
        dataset_count = len(procdataset_names)
        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                peaks_crt = mh5.load_dataset(h5file, self.h5writepath + '/grouped_rts')
                mh5.save_dataset(h5file, self.h5writepath + '/merged_grouped_rts',peaks_crt)
                peaks_cmz = mh5.load_dataset(h5file, self.h5writepath + '/grouped_cmz')
                
                # identify common retention time vector
                n_crt     = len(peaks_crt)
                n_cmz     = len(peaks_cmz)
                n_samples = len(procdataset_names)
                
                # compile data matrix for deconvolution across all samples       
                if self.h5writepath + '/merged_X_3D' in h5file:
                     X_3D = h5file[self.h5writepath + '/merged_X_3D'];
                     X_3D.resize((n_samples, n_cmz, n_crt));
                else:
                     X_3D = h5file.create_dataset(self.h5writepath + '/merged_X_3D', shape = (n_samples, n_cmz, n_crt), maxshape = (None, None, None),
                                                           chunks = True, compression="gzip", 
                                                           compression_opts = 5, dtype = np.float64);                
                                                           
                                                           
                # compile data matrix for deconvolution across all samples       
                if self.h5writepath + '/X_3D' in h5file:
                     dc_X_3D = h5file[self.h5writepath + '/X_3D'];
                     dc_X_3D.resize((n_samples, n_cmz, n_crt));
                else:
                     dc_X_3D = h5file.create_dataset(self.h5writepath + '/X_3D', shape = (n_samples, n_cmz, n_crt), maxshape = (None, None, None),
                                                           chunks = True, compression="gzip", 
                                                           compression_opts = 5, dtype = np.float64);                                                           
                                                           
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    peaks  = mh5.load_dataset(h5file, \
                                                     self.h5writepath + datasetid + '/grouped_peaks')
                    speaks = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()
                    
                    X_3D[dataset_ind, :, :] = speaks.transpose()
                   
                    printlog('%s. %s: Performing 3D matrix reconstruction for deconvolution: Saved to --> %s' \
                          %(dataset_ind + 1, datasetid, self.h5writepath)) 
                             
                # peak integrals (i.e. scores)
                if self.h5writepath + '/quantity_integrals' in h5file:
                    q_i = h5file[self.h5writepath + '/quantity_integrals']
                    q_i.resize((n_samples, n_crt))
                else:
                    q_i = h5file.create_dataset(self.h5writepath + '/quantity_integrals', shape = (n_samples, n_crt), maxshape = (n_samples, None),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64)
                    
                # fragmenation MS spectra (i.e. loadings)
                if self.h5writepath + '/integral_MS_spectra' in h5file:
                    frag_pattern = h5file[self.h5writepath + '/integral_MS_spectra']
                    frag_pattern.resize((n_crt, n_cmz))
                else:
                    frag_pattern = h5file.create_dataset(self.h5writepath + '/integral_MS_spectra', shape = (n_crt,n_cmz), maxshape = (None, n_cmz),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64)


                # deconvolution info
                # original rt index, original rt, new rt index, new rt, component index, variance, partial variance
                if self.h5writepath + '/group_variance' in h5file:
                    group_variance = h5file[self.h5writepath + '/group_variance']
                    group_variance.resize((n_crt, 8))
                else:
                    group_variance = h5file.create_dataset(self.h5writepath + '/group_variance', shape = (n_crt, 8), maxshape = (None, 8),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64)


                total_comp = 0    
                for i in range(n_crt):
                    printlog('Performing deconvolution of %s rt peak of %s total rt peaks...'%(i+1, n_crt));
                    # exctract data matrix for each chromatographic peak
                    X = np.array(X_3D[:, :, i])
                    denom  = np.sum(np.power(X, 2))
                    
                    original_rt = peaks_crt[i];
                    
                    # adaptively estimate the number of co-eluting components for each chromatographic peak
                    nmf_cum_variance = np.array([])
                    max_comps, dim = X.shape
                    i_comp = 0
                    while True:
                        i_comp = i_comp + 1
                        nmf_model = NMF(n_components = i_comp, init='nndsvd')
                        Wcur = nmf_model.fit_transform(X)  # quantity integrals 
                        Hcur = nmf_model.components_       # integral spectra (fragmentation patterns/spectra)
                        # Cumulative variance calculation
                        cum_var = np.round(100*
                                                (1 - np.sum(
                                                            np.power(
                                                                    X - np.dot(
                                                                                np.matrix(Wcur), np.matrix(Hcur)
                                                                               ), 
                                                                    2)
                                                            )/denom
                                                )
                                          )
                        
                        nmf_cum_variance = np.append(nmf_cum_variance, cum_var);
                        
                        if i_comp == 1:                            
                            Hbest = Hcur
                            Wbest = Wcur
                            prev_Hbest = Hbest;
                            prev_Wbest = Wbest;
                        else:
                            
                            if i_comp >= max_comps:
                                i_comp -= 1
                                break
                            
                            if nmf_cum_variance[i_comp-1] - nmf_cum_variance[i_comp-2] < 5.0:
                                i_comp -= 1
                                break
                            
                            if i_comp > 2:
                                # linear decrease in component variance is likely due to chance
                                comp_diff1 = nmf_cum_variance[i_comp-1] - nmf_cum_variance[i_comp-2]
                                comp_diff2 = nmf_cum_variance[i_comp-2] - nmf_cum_variance[i_comp-3]    
                                if  comp_diff1 == comp_diff2:
                                    i_comp -= 2;
                                    Hbest = prev_Hbest;
                                    Wbest = prev_Wbest;
                                    break
                            
                            prev_Hbest = Hbest;
                            Hbest = Hcur
                            prev_Wbest = Wbest;
                            Wbest = Wcur
                            
                    total_comp += i_comp;    
                    
                    if total_comp > n_crt:
                        q_i.resize((n_samples, total_comp))
                        frag_pattern.resize((total_comp, n_cmz))
                        group_variance.resize((total_comp, 8));
                        dc_X_3D.resize((n_samples, n_cmz, total_comp))
                                            
                    #This section removes the need for cycling through components and allows for sorting by explained variance
                    restored_comp = np.ones((Wbest.shape[0], Hbest.shape[1], i_comp));
                    restored_comp = np.multiply(restored_comp, np.array(Wbest).reshape((Wbest.shape[0], 1, Wbest.shape[1])));
                    restored_comp = np.multiply(restored_comp, np.array(Hbest.transpose()).reshape((1, Hbest.shape[1], Hbest.shape[0])));
                    
                    # normalize fragmentation pattern
                    ifrag_pattern = Hbest
                    pattern_max   = ifrag_pattern.max(1).astype(float)
                    pattern_max[pattern_max < 1] = 1.
                    pattern_max   = 1./pattern_max
                    ifrag_pattern = ifrag_pattern * pattern_max[:, None]
                    ifrag_pattern[ifrag_pattern < 0.00001] = 0.
                    
                    quantity_integrals = np.sum(restored_comp, axis = 1);                    
                    mean_intens = np.mean(quantity_integrals, axis = 0);
                    total_intens = np.sum(quantity_integrals);
                    
                    if total_intens < 1e-9:
                        total_intens = 1.0;

                    explained_intensity = np.round(100 * np.sum(quantity_integrals, axis = 0) / total_intens);
                    
                    #Sorting by explained intensity in decreasing order                    
                    order_index = np.argsort(100 - explained_intensity);
                    
                    mean_intens = mean_intens[order_index];
                    explained_intensity = explained_intensity[order_index];
                    quantity_integrals = quantity_integrals[:, order_index];
                    restored_comp = restored_comp[:, :, order_index];
                    ifrag_pattern = ifrag_pattern[order_index, :];
                    
                    #grouped variance update
                    group_variance[total_comp - i_comp : total_comp, 0] = i;
                    group_variance[total_comp - i_comp : total_comp, 1] = original_rt;
                    group_variance[total_comp - i_comp : total_comp, 2] = np.arange(total_comp - i_comp, total_comp);
                    group_variance[total_comp - i_comp : total_comp, 3] = original_rt;
                    group_variance[total_comp - i_comp : total_comp, 4] = nmf_cum_variance[0 : i_comp];
                    group_variance[total_comp - i_comp : total_comp, 5] = np.mean(np.sum(X, axis = 1));
                    group_variance[total_comp - i_comp : total_comp, 6] = mean_intens;
                    group_variance[total_comp - i_comp : total_comp, 7] = explained_intensity;
                    
                    q_i[:, total_comp - i_comp : total_comp] = quantity_integrals
                    dc_X_3D[:, :, total_comp - i_comp : total_comp] = restored_comp
                    frag_pattern[total_comp - i_comp : total_comp, :] = ifrag_pattern

                mh5.save_dataset(h5file, self.h5writepath + '/grouped_rts', data = group_variance[:, 3], compression_opts = 5);
                    
                h5file[self.h5writepath].attrs['deconvolved'] = True
                
                dataset_ind = -1    
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    peak_integrals =  np.array(q_i[dataset_ind, :]).flatten()
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/quantity_integrals',\
                                             data = peak_integrals, compression_opts = 5)
                    h5file[self.h5writepath + datasetid].attrs['deconvolved'] = True;
               
    def get_peak_integrals_individual(self,procdataset_names):
        """    
        Performs integral calculations for chromatographic peaks of individual profiles
        
        """
        #tic();
        dataset_count = len(procdataset_names)
        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                h5file[self.h5writepath].attrs['individual'] = True;
                #TODO: Check which is better for quantity assessment
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    h5file[self.h5writepath + datasetid].attrs['individual'] = True;
                    peaks_crt = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/grouped_rts')
                    peaks_cmz = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/grouped_cmz')
                
                    # identify common retention time vector
                    n_crt = len(peaks_crt)
                    n_cmz = len(peaks_cmz)
     
                    peaks  = mh5.load_dataset(h5file, \
                                                     self.h5writepath + datasetid + '/grouped_peaks')
                    speaks = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()
                    
                    peak_integrals  = np.array(speaks.sum(1)).astype(float).flatten()

                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/quantity_integrals',\
                                             data = peak_integrals, compression_opts = 5)
                    
                    h5file[self.h5writepath + datasetid].attrs['deconvolved'] = False;

                    printlog('%s. %s: Performing integration of chromatographic peaks: Saved to --> %s' \
                              %(dataset_ind, datasetid, self.h5writepath))      
        
                h5file[self.h5writepath].attrs['deconvolved'] = False; 

    def get_peak_integrals(self,procdataset_names):
        """    
        Performs integral calculations for chromatographic peaks of all profiles
        
        """
        #tic();
        dataset_count = len(procdataset_names)
        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                peaks_crt = mh5.load_dataset(h5file, self.h5writepath + '/grouped_rts')
                peaks_cmz = mh5.load_dataset(h5file, self.h5writepath + '/grouped_cmz')
                
                # identify common retention time vector
                n_crt = len(peaks_crt)
                n_cmz = len(peaks_cmz)
                
                #TODO: Check which is better for quantity assessment
                if self.params['occurence'] == 'all':
                    pass
                elif self.params['occurence'] == 'common':
                    mask = np.zeros([n_crt,n_cmz])        
                    
                    dataset_ind = -1
                    for datasetid in procdataset_names:
                        dataset_ind = dataset_ind + 1
                        peaks     = mh5.load_dataset(h5file, \
                                                     self.h5writepath + datasetid + '/grouped_peaks')
                        speaks    = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray() 
                                                        
                        speaks_max = speaks.max(1).astype(float)
                        speaks_max[speaks_max < 1] = 1.
                        speaks_max  = 1./speaks_max
                        speaks = speaks * speaks_max[:,None]
                        mask[speaks > 0.05] += 1;
                    
                    for i in np.arange(0,n_crt):
                        row_vals = np.array(mask[i,:]).flatten()
                        indices = np.where(row_vals == row_vals.max())
                        mask[i, :] = 0  
                        mask[i, indices] = 1
                
                
                if self.h5writepath + '/quantity_integrals' in h5file:
                    q_i = h5file[self.h5writepath + '/quantity_integrals'];
                    q_i.resize((len(procdataset_names), n_crt));
                else:
                    q_i = h5file.create_dataset(self.h5writepath + '/quantity_integrals', shape = (len(procdataset_names), n_crt), maxshape = (None, None),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64);                
                if self.h5writepath + '/X_3D' in h5file:
                     X_3D = h5file[self.h5writepath + '/X_3D'];
                     X_3D.resize((len(procdataset_names),n_cmz, n_crt));
                else:
                     X_3D = h5file.create_dataset(self.h5writepath + '/X_3D', shape = (len(procdataset_names), n_cmz, n_crt), maxshape = (None, None, None),
                                                           chunks = True, compression="gzip", 
                                                           compression_opts = 5, dtype = np.float64);                
                                                           
                h5file[self.h5writepath].attrs['deconvolved'] = False; 
                                                           
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    peaks  = mh5.load_dataset(h5file, \
                                                     self.h5writepath + datasetid + '/grouped_peaks')
                    speaks = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()
                                                        
                    #X_3D[dataset_ind, :,:] = speaks.transpose()
                    speaks_start_rt = sparse.csr_matrix((peaks[7,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()
                    speaks_peak_rt = sparse.csr_matrix((peaks[6,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()
                    speaks_end_rt = sparse.csr_matrix((peaks[8,:],(peaks[2,:],peaks[4,:])),\
                                                        shape=(n_crt,n_cmz)).toarray()

                    if 'mask' in locals():
                        speaks = speaks * mask
                        speaks_start_rt = speaks_start_rt * mask
                        speaks_peak_rt = speaks_peak_rt * mask
                        speaks_end_rt = speaks_end_rt * mask

                    speaks_width_max = np.max(speaks_end_rt - speaks_start_rt, axis = 1);
                    
                    speaks_a = speaks_end_rt - speaks_peak_rt;
                    speaks_b = speaks_peak_rt - speaks_start_rt;
                    
                    mask = np.logical_and(speaks_a > 0.0, speaks_b > 0.0);
                    
                    scew = np.zeros(speaks.shape, dtype = np.float64);
                    
                    scew[mask] = np.log(np.divide(speaks_b[mask], speaks_a[mask]));
                    
                    scew_neg = np.sign(scew);
                    
                    scew_abs = np.abs(scew);
                    
                    #TODO: finish diagnostics
                        
                    X_3D[dataset_ind, :, :] = speaks.transpose()
                    
                    peak_integrals  = np.array(speaks.sum(1)).astype(float).flatten()
                    
                    q_i[dataset_ind,:] = peak_integrals
                    
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/quantity_integrals',\
                                             data = peak_integrals, compression_opts = 5)
                                             
                    h5file[self.h5writepath + datasetid].attrs['deconvolved'] = False;
                         
                    printlog('%s. %s: Performing integration of chromatographic peaks: Saved to --> %s' \
                              %(dataset_ind, datasetid, self.h5writepath)) 
                              
    def extract_fragment_patterns_individual(self, procdataset_names):
        """    
        Performs fragmentaion pattern exctraction of chromatographic peaks of individual profiles
            
        """   
        # fragmentation pattern exctraction
        dataset_count = len(procdataset_names)
        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    peaks_crt = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/grouped_rts')
                    peaks_cmz = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/grouped_cmz')
                
                    # identify common retention time
                    n_crt = len(peaks_crt)
                    n_cmz = len(peaks_cmz)
                    
                    peaks     = mh5.load_dataset(h5file, \
                                                 self.h5writepath + datasetid + '/grouped_peaks')
                                                 
                    speaks      = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                    shape=(n_crt,n_cmz)).toarray()

                    speaks_sum  = speaks.sum(1).astype(float).flatten()
                    
                    #TODO: Check which is better for annotation                    
                    speaks_sum[speaks_sum<1] = 1.
                    speaks_sqrt = 1./np.sqrt(speaks_sum)
                        
                    #TODO: Check if needed at the annotation stage
                    speaks       = speaks * speaks_sqrt[:,None]
                    frag_pattern = speaks
                    
                    printlog('%s. %s: Performing fragmentation pattern exctraction from --> %s' \
                              %(dataset_ind, datasetid, self.h5writepath)) 
                
                    #Normalization for the maximum peak to be 1.
                    pattern_max = frag_pattern.max(1).astype(float)
                    pattern_max[pattern_max<1] = 1.
                    pattern_max = 1./pattern_max
                    frag_pattern = frag_pattern*pattern_max[:,None]
                
                    #TODO: Adjust here for the threshold for best annotation scores
                    frag_pattern[frag_pattern<0.00001] = 0.
                    
                    mh5.save_dataset(h5file, self.h5writepath  + datasetid + '/integral_MS_spectra',\
                                             data = frag_pattern, compression_opts = 5)   
                
    def extract_fragment_patterns(self, procdataset_names):
        """    
        Performs fragmentaion pattern exctraction of chromatographic peaks of all profiles
            
        """   
        # fragmentation pattern exctraction
        dataset_count = len(procdataset_names)
        if dataset_count>0:
            with h5py.File(self.dbfilepath, 'a') as h5file:
                peaks_crt = mh5.load_dataset(h5file, self.h5writepath + '/grouped_rts')
                peaks_cmz = mh5.load_dataset(h5file, self.h5writepath + '/grouped_cmz')
                
                # identify common retention time
                n_crt = len(peaks_crt)
                n_cmz = len(peaks_cmz)
                
                if self.params['frag_pattern']=='max':
                    crt_max_int       = np.zeros([n_crt])            
                
                frag_pattern  = np.zeros([n_crt,n_cmz])
                
                dataset_ind = -1
                for datasetid in procdataset_names:
                    dataset_ind = dataset_ind + 1
                    peaks     = mh5.load_dataset(h5file, \
                                                 self.h5writepath + datasetid + '/grouped_peaks')
                    speaks      = sparse.csr_matrix((peaks[0,:],(peaks[2,:],peaks[4,:])),\
                                                    shape=(n_crt,n_cmz)).toarray()
                    speaks_sum  = speaks.sum(1).astype(float).flatten()
                    
                    #TODO: Check which is better for annotation                    
                    if self.params['frag_pattern']=='max':
                        if sum(speaks_sum>crt_max_int)>0:
                            frag_pattern[speaks_sum>crt_max_int,:] = speaks[speaks_sum>crt_max_int,:]
                            crt_max_int[speaks_sum>crt_max_int] = speaks_sum[speaks_sum>crt_max_int]
                    elif self.params['frag_pattern']=='aggregate':
                        speaks_sum[speaks_sum<1] = 1.
                        speaks_sqrt = 1./np.sqrt(speaks_sum)
                        
                        #TODO: Check if needed at the annotation stage
                        speaks       = speaks * speaks_sqrt[:,None]
                        frag_pattern = frag_pattern + speaks
                    
                    printlog('%s. %s: Performing fragmentation pattern exctraction from --> %s' \
                              %(dataset_ind, datasetid, self.h5writepath)) 
                
                #Normalization for the maximum peak to be 1.
                pattern_max = frag_pattern.max(1).astype(float)
                pattern_max[pattern_max<1] = 1.
                pattern_max = 1./pattern_max
                frag_pattern = frag_pattern*pattern_max[:,None]
                
                #TODO: Adjust here for the threshold for best annotation scores
                frag_pattern[frag_pattern<0.00001] = 0.
                
                mh5.save_dataset(h5file, self.h5writepath  + '/integral_MS_spectra',\
                                         data = frag_pattern, compression_opts = 5)   
                              
    def cluster_rts_kernel(self, procdataset_names):
        """    
        Performs clustering of chromatographic peaks by means of kernel-density approach of all profiles
            
        """       
        with h5py.File(self.dbfilepath, 'a') as h5file:
            printlog('\n...Chromatographic peak clustering: Calculating common retention time vector (cluster centroids)...\n')
            self.__rtvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'crt')     
            self.__mzvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'cmz')
            dataset_count = len(procdataset_names)
            histc         = np.zeros([1,len(self.__rtvals)-1]).flatten()
            if dataset_count>0:
                dataset_index = -1
                peak_widths   = []
                
                # identify common retention time vector by iteratively caclulating histogram of 
                # detected peaks across samples 
                for datasetid in procdataset_names:
                    dataset_index += 1;
                    peaks       = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/sp_unfiltered_peaks')
                    pass_filter = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/peaks_pass_filter')
                    peaks       = peaks[:, pass_filter==1] 
                    peak_widths.append(np.median(peaks[10,:]))
                    
                    if self.params['weighted_density']=='yes':
                        peak_weights = np.divide(peaks[2,:],np.sum(peaks[2,:]))                   
                        histc = histc + np.histogram(peaks[2,:].flatten(),self.__rtvals,\
                                                         weights = peak_weights)[0]
                    else:
                        histc = histc + np.histogram(peaks[2,:].flatten(),self.__rtvals)[0].flatten()
                        
                # extract tolerance for retention time grouping if not specified        
                if str(self.params['rt_tol']).lower() == 'auto':
                    self.params['rt_tol'] = np.median(np.array(peak_widths).astype(float))/5
                    
                rt_tol = np.divide(self.params['rt_tol'],self.__rtvals[1]-self.__rtvals[0])
                
                # identify peak clusters/groups of similar rt values
                peak_finder     = PeakFinder('','','')
                self.peak_indcs = peak_finder.findpeakmaxs(histc.flatten(),gap = int(rt_tol))
               
                # remove peak clusters present in a small proportion of samples
                histc_threshold = np.float64(max(median_threshold(histc) * 0.05, 5));
                print(histc_threshold)
                print(type(histc_threshold))
                print(np.min(histc))
                print(np.max(histc))
               
                #histc_threshold = ;
                self.peak_indcs = self.peak_indcs[histc[self.peak_indcs] > histc_threshold];
                
                # the peak retention time values define common retention time vector
                crt = self.__rtvals[self.peak_indcs]
                crt = crt.flatten();
                
                # now align each of your sample datasets to the common one using nearest-neighbour approach
                peak_widths   = []
                
                #Reference indeces to utf_8 array holding dataset names (needed for future consistency of indexing if any names are changed/added/re-sorted etc.)
                if self.h5writepath + '/dataset_names' in h5file:
                    dataset_names = h5file[self.h5writepath + '/dataset_names'];
                    dataset_names.resize((len(procdataset_names), 2));
                else:
                    dataset_names = h5file.create_dataset(self.h5writepath + '/dataset_names', shape = (len(procdataset_names), 2), 
                                                      chunks = (10000, 2), maxshape=(None, 2), compression="gzip", compression_opts = 5, 
                                                      dtype = np.uint64);
                                                      
                #to read back use: h5read_strings from utils/h5utils
                
                #utf_8 array to hold strings
                if self.h5writepath + '/utf_8' in h5file:
                    utf_8 = h5file[self.h5writepath + '/utf_8'];
                else:
                    utf_8 = h5file.create_dataset(self.h5writepath + '/utf_8', shape = (1, ), maxshape = (None, ),
                                                      chunks = (100000, ), compression="gzip", 
                                                      compression_opts = 5, dtype = np.uint8);
                                                      
                dataset_index = -1
                mean_peak_width = 0.0;                    

                for datasetid in procdataset_names:
                    dataset_index += 1;
                    peaks       = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/sp_unfiltered_peaks')
                    pass_filter = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/peaks_pass_filter')
                    peaks       = peaks[:, pass_filter==1] 
                    
                    rt = peaks[2, :].flatten()
                    
                    # efficient nearest-neighbour alignment of retention time vector to the common feature vector
                    rt2crtindcs = np.round(np.interp(rt, crt, np.arange(0., len(crt))))
                    rt2crtindcs = (rt2crtindcs.astype(int)).flatten()
                    
                    # remove all matched pairs smaller than pre-defined or calculated torelance 
                    matched_rt_indcs  = np.asarray(np.nonzero(np.abs(crt[rt2crtindcs]-rt)<=self.params['rt_tol']))
                    matched_rt_indcs  = (matched_rt_indcs.astype(int)).flatten()
                    crt_indcs = rt2crtindcs[matched_rt_indcs]
                    nn_rt     = crt[crt_indcs]
                    peaks     = peaks[:,matched_rt_indcs]
                    
                    # save grouped/clustered peaks
                    #gr_peaks  = np.zeros([7, len(matched_rt_indcs)])
                    gr_peaks  = np.zeros([9, len(matched_rt_indcs)])
                    gr_peaks[0,:] = peaks[0, :]  # peak integral
                    gr_peaks[1,:] = nn_rt       # peak retention time value
                    gr_peaks[2,:] = crt_indcs   # peak retention time index
                    gr_peaks[3,:] = peaks[11, :] # peak m/z value
                    gr_peaks[4,:] = peaks[12, :] # peak m/z index
                    gr_peaks[5,:] = dataset_index; #peak dataset index
                    gr_peaks[6,:] = peaks[2, :] #original rt value
                    gr_peaks[7,:] = peaks[1, :] #peak start rt value
                    gr_peaks[8,:] = peaks[3, :] #peak end rt value
                    
                    mean_peak_width += np.median(peaks[10, :]);
                        
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/grouped_peaks',\
                                             data = gr_peaks, compression_opts = 5)
                    
                    printlog('%s. %s: Performing alignment of chromatographic peaks to cluster centroids: Saved to --> %s' \
                              %(dataset_index, datasetid, self.h5writepath)) 
                
                h5file[self.h5writepath].attrs['mean_peak_width'] = mean_peak_width/len(procdataset_names);
                
                pset = [];             
                for s in procdataset_names:
                    pset.append(s.lstrip('/'));
                    
                h5write_strings(dataset_names, utf_8, pset, overwrite = True);

                mh5.save_dataset(h5file, self.h5writepath + '/grouped_rts', data = crt)
                mh5.save_dataset(h5file, self.h5writepath + '/grouped_cmz', data = self.__mzvals)
                mh5.save_dataset(h5file, self.h5writepath + '/clustering_histogram', data = histc)
                mh5.save_dataset(h5file, self.h5writepath + '/clustering_histogram_threshold', data = histc_threshold)
                                
    def cluster_individual_rts_kernel(self, procdataset_names):
        """    
        Performs clustering of chromatographic peaks by means of kernel-density approach.
        Does clustering on the per sample basis
            
        """       
        with h5py.File(self.dbfilepath, 'a') as h5file:
            dataset_count = len(procdataset_names)
            if dataset_count>0:
                dataset_index = -1
                peak_widths   = []
                self.__rtvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'crt')     
                self.__mzvals = mh5.load_dataset(self.dbfilepath, self.h5readpath + 'cmz')
                mean_peak_width = 0.0;    
                accum_peak_indcs = np.zeros((0,), dtype = np.int64);
                
                # identify common retention time vector by iteratively caclulating histogram of 
                # detected peaks across samples 
                for datasetid in procdataset_names:
                    
                    printlog('\n...Chromatographic peak clustering: Calculating common retention time vector (cluster centroids)...\n')
                    #histc         = np.zeros([1,len(self.__rtvals)-1]).flatten()                    
                    
                    dataset_index += 1;
                    peaks       = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/sp_unfiltered_peaks')
                    pass_filter = mh5.load_dataset(h5file, self.h5writepath + datasetid + '/peaks_pass_filter')
                    peaks       = peaks[:, pass_filter==1] 
                    peak_widths.append(np.median(peaks[10,:]))
                    
                    if self.params['weighted_density']=='yes':
                        peak_weights = np.divide(peaks[2,:], np.sum(peaks[2,:]))                   
                        histc = np.histogram(peaks[2,:].flatten(),self.__rtvals,\
                                                         weights = peak_weights)[0]
                        histc = histc.flatten()
                    else:
                        histc = np.histogram(peaks[2,:].flatten(),self.__rtvals)[0].flatten()
                        
                    # extract tolerance for retention time grouping if not specified        
                    if str(self.params['rt_tol']).lower() == 'auto':
                        self.params['rt_tol'] = np.median(np.array(peak_widths).astype(float))/5
                        
                    rt_tol = np.divide(self.params['rt_tol'],self.__rtvals[1]-self.__rtvals[0])
                    
                    # identify peak clusters/groups of similar rt values
                    peak_finder     = PeakFinder('','','')
                    self.peak_indcs = peak_finder.findpeakmaxs(histc.flatten(), gap = int(rt_tol))
                   
                    # remove peak clusters present in a small proportion of samples
                    histc_threshold = median_threshold(histc);
                    self.peak_indcs = self.peak_indcs[histc[self.peak_indcs] > histc_threshold]
                    
                    # the peak retention time values define common retention time vector
                    accum_peak_indcs = np.unique(np.hstack([accum_peak_indcs, self.peak_indcs]));
                    crt = self.__rtvals[self.peak_indcs]
                    crt = crt.flatten();
                    
                    rt = peaks[2, :].flatten()
                    
                    # efficient nearest-neighbour alignment of retention time vector to the common feature vector
                    rt2crtindcs = np.round(np.interp(rt, crt, np.arange(0., len(crt))))
                    rt2crtindcs = (rt2crtindcs.astype(int)).flatten()
                    
                    # remove all matched pairs smaller than pre-defined or calculated torelance 
                    matched_rt_indcs  = np.asarray(np.nonzero(np.abs(crt[rt2crtindcs]-rt)<=self.params['rt_tol']))
                    matched_rt_indcs  = (matched_rt_indcs.astype(int)).flatten()
                    crt_indcs = rt2crtindcs[matched_rt_indcs]
                    nn_rt     = crt[crt_indcs]
                    peaks     = peaks[:,matched_rt_indcs]
                    
                    # save grouped/clustered peaks
                    gr_peaks  = np.zeros([7,len(matched_rt_indcs)])
                    gr_peaks[0,:] = peaks[0,:]  # peak integral
                    gr_peaks[1,:] = nn_rt       # peak retention time value
                    gr_peaks[2,:] = crt_indcs   # peak retention time index
                    gr_peaks[3,:] = peaks[11,:] # peak m/z value
                    gr_peaks[4,:] = peaks[12,:] # peak m/z index
                    gr_peaks[5,:] = dataset_index; #peak dataset index
                    gr_peaks[6,:] = peaks[2, :] #original rt value
                    
                    mean_peak_width += np.median(peaks[10, :]);
                        
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/grouped_peaks',\
                                             data = gr_peaks, compression_opts = 5)

                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/grouped_rts', data = crt)
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/grouped_cmz', data = self.__mzvals)
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/clustering_histogram', data = histc)
                    mh5.save_dataset(h5file, self.h5writepath + datasetid + '/clustering_histogram_threshold', data = histc_threshold)

                    printlog('%s. %s: Performing per sample alignment of chromatographic peaks to cluster centroids: Saved to --> %s' \
                              %(dataset_index, datasetid, self.h5writepath)) 

                #Reference indeces to utf_8 array holding dataset names (needed for future consistency of indexing if any names are changed/added/re-sorted etc.)
                if self.h5writepath + '/dataset_names' in h5file:
                    dataset_names = h5file[self.h5writepath + '/dataset_names'];
                    dataset_names.resize((len(procdataset_names), 2));
                else:
                    dataset_names = h5file.create_dataset(self.h5writepath + '/dataset_names', shape = (len(procdataset_names), 2), 
                                                          chunks = (10000, 2), maxshape=(None, 2), compression="gzip", compression_opts = 5, 
                                                          dtype = np.uint64);
                                                          
                #to read back use: h5read_strings from utils/h5utils
                
                #utf_8 array to hold strings
                if self.h5writepath + '/utf_8' in h5file:
                    utf_8 = h5file[self.h5writepath + '/utf_8'];
                else:
                    utf_8 = h5file.create_dataset(self.h5writepath + '/utf_8', shape = (1, ), maxshape = (None, ),
                                                      chunks = (100000, ), compression="gzip", 
                                                      compression_opts = 5, dtype = np.uint8);
                
                h5file[self.h5writepath].attrs['mean_peak_width'] = mean_peak_width/len(procdataset_names);
                
                pset = [];             
                for s in procdataset_names:
                    pset.append(s.lstrip('/'));
                    
                h5write_strings(dataset_names, utf_8, pset, overwrite = True);
                
                accum_crt = self.__rtvals[accum_peak_indcs];
                
                accum_crt = accum_crt.flatten();
    
                mh5.save_dataset(h5file, self.h5writepath + '/grouped_rts', data = accum_crt)
                mh5.save_dataset(h5file, self.h5writepath + '/grouped_cmz', data = self.__mzvals)
                    
def finalize_metadata(dbfilepath, h5readpath, h5writepath, proc_dataset_names):
    if proc_dataset_names:
        with h5py.File(dbfilepath, 'a') as h5file:
            for i in range(len(proc_dataset_names)):
                datasetid = proc_dataset_names[i];
                
                target_gname = h5writepath + datasetid;
                source_gname = h5readpath + datasetid;
    
                wgroup = h5file[target_gname];
                sgroup = h5file[source_gname];
                    
                wgroup.attrs['is_raw'] = False;
                wgroup.attrs['is_OK'] = True;
                wgroup.attrs['is_processed'] = True;
                wgroup.attrs['is_continuous'] = False;
                wgroup.attrs['has_integrals'] = True;
                wgroup.attrs['is_sample_dataset'] = True;
                wgroup.attrs['parent'] = np.string_(source_gname)
                mh5.copy_meta_over(sgroup, wgroup);


def vis_detected_peaks(rtvals,ics,peak_params):
    
    from matplotlib.pyplot import cm  
    import matplotlib.pyplot as plt   
    nsp,nmz = ics.shape     
    color   = iter(cm.rainbow(np.linspace(0,1,nmz))) 
    for i in range(nmz):       
        sp_indices = peak_params[5,:]==i
        if np.sum(sp_indices) == 0:
            continue
        else: 
            ipeak_params = peak_params[:,sp_indices]
           
        c = next(color)     
        plt.plot(rtvals,ics[:,i],c=c)     
        plt.scatter(rtvals[ipeak_params[2,:].astype(int)],ics[ipeak_params[2,:].astype(int),i],c=c)     
        plt.scatter(rtvals[ipeak_params[3,:].astype(int)],ics[ipeak_params[3,:].astype(int),i],c=c,marker='s')     
        plt.scatter(rtvals[ipeak_params[4,:].astype(int)],ics[ipeak_params[4,:].astype(int),i],c=c,marker='s')


def median_threshold(X):
        md = np.median(X);
        MAD = np.median(np.abs(np.subtract(X, md))) * 1.4826;
        thr = md + 3*MAD;
        return thr



if __name__ == "__main__": 
    tic();
    settings = OptionsHolder(__doc__, PeakDetection_options) 
    settings.description = 'Peak Detection'   
    settings.do = 'yes'   
    printlog(settings.program_description)   
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
    printlog(settings.format_parameters())   
   
    #do_peak_detection(settings.parameters['dbfilename'],\
    #                 method = settings.parameters['method'], \
    #                 params = settings.parameters['params'])
    

    do_peak_detection(settings.parameters)
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();#
    printlog(settings.description_epilog);
    stop_log();
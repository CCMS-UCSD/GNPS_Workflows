# -*- coding: utf-8 -*-
"""
*******************************************************************
Re-import results and reconstruct the data matrix from TIC and
fragmentation patterns
*******************************************************************

This module is designed to back-port the exported results in the form
of TIC.csv table and fragmentation pattern in either NIST (*.txt) or 
GNPS (*.mgf) formats. 


run python.exe <re_import>.py --help to get info about parameters of the script


"""


#===========================Import section=================================

#Importing standard and external modules
import os; 
import sys;
import traceback #This is for displaying traceback in try: except: constructs
import time;

import h5py
import numpy as np

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        #Use print here instead of printlog as printlog is not yet imported! 
        #The rest should have printlog in place of print.
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path); 
    

#Import local/internal modules
from proc.procconfig import ReImport_Results_options as cmdline_options;
import proc.io.manageh5db as mh5

#Manager for command line options
from proc.utils.cmdline import OptionsHolder
#Timing functions for standard stats output
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.matching import match_lists, nn_match, condense_with_tolerance;
from proc.utils.h5utils import h5write_strings;

#==========================================================================
#From here the main code starts

        


def load_tic_file(ticfilename):
    dataset_names = [];
    data_values = [];
    rts = [];
    mzs = [];
    intfrac = [];
    #relmaxint = [];
    bestorder = [];
    deconvoluted = False;
    
    with open(ticfilename, 'r') as finp:
        index = -1;
        for s in finp:
            index += 1;
            s = s.rstrip().rstrip(',').split(',');
            if index == 0:
                for i in range(1, len(s)):
                    ss = s[i];
                    if ss.startswith('peak'):
                        ss = ss.split('_')[1];
                        ss = ss.split(' min');
                        rt = ss[0];
                        if 'mz' in ss[1]:
                            mz = ss[1].split('mz ')[1];
                        else:
                            mz = 0.0;
                        fint = 100.0;

                    elif '(' in ss:
                        ss = ss.split(' (');
                        rt = ss[0];
                        fint = ss[1].split('%)')[0];
                        mz = 0.0;
                        deconvoluted = True;
                        
                    else:
                        rt = ss;
                        mz = 0.0;
                        fint = 100.0;
                        
                    try:
                        rt = float(rt);
                    except:
                        printlog('Error! "%s" cannot be converted to float!'%rt);
                        return None;
                            
                    try:
                        mz = float(mz);
                    except:
                        printlog('Error! "%s" cannot be converted to float!'%mz);
                        return None

                    try:
                        fint = float(fint);
                    except:
                        printlog('Error! "%s" cannot be converted to float!'%fint);
                        return None

                    rts.append(rt);
                    mzs.append(mz);
                    intfrac.append(fint);
            
            elif s[0].startswith('Rel. Max Integral:'):
                pass
                #for i in range(1, len(s)):
                #    try:
                #        relmaxint.append(float(s[i]))
                #    except:
                #        printlog('Error! "%s" cannot be converted to float!'%s[i]);
            
            elif s[0].startswith('Sample\Best Order:'):
                pass
                #for i in range(1, len(s)):
                #    try:
                #        bestorder.append(int(s[i]))
                #    except:
                #        printlog('Error! "%s" cannot be converted to integer!'%s[i]);
                        
            else:
                if s[0] != '':
                    dataset_names.append(s[0])
                    data = [];
                    for i in range(1, len(s)):
                        try:
                            if ('NA' in s[i]) or ('N/A' in s[i]):
                                data.append(0.0);
                            else:
                                data.append(float(s[i]))
                        except:
                            printlog('Error! "%s" cannot be converted to float!'%s[i]);
                            
                    data_values.append(data);
                                                
                                                
    rts = np.array(rts, dtype = np.float64);
    data_values = np.array(data_values, dtype = np.float64);
    mzs = np.array(mzs, dtype = np.float64);
    intfrac = np.array(intfrac, dtype = np.float64);
    
    #if relmaxint:
    #    relmaxint = np.array(relmaxint, dtype = np.float64);
    #else:
    #    maxint = np.max(data_values[data_values > 0.0]);
    #    maxi = np.max(data_values, axis = 0);
    #    if maxint == 0.0:
    #        maxint = 1.0;
    #    relmaxint = maxi / maxint * 100;
        
    #if bestorder:
    #    bestorder = np.array(bestorder, dtype = np.float64);
    #else:
    #    order = np.argsort(-relmaxint);
    #    bestorder = np.zeros(order.shape, dtype = np.int64);
    #    bestorder[order] = np.arange(1, order.shape[0] + 1, dtype = np.int64);
                            
    return rts, dataset_names, data_values, mzs, intfrac, deconvoluted
    
    
    

def load_mgf_fragments(fragfilename):
    rt_peaks = [];
    ms_fragments = [];
    reading_peaks = False;
    in_record = False;
    current_ms_fragments = [];
    current_rt = 0.0;
    with open(fragfilename, 'r') as finp:
        for s in finp:
            s = s.rstrip('\n');
            if in_record:
                if reading_peaks:
                    if s.startswith('END'):
                        reading_peaks = False;
                        in_record = False;
                        ms_fragments.append(current_ms_fragments);
                        rt_peaks.append(current_rt);
                        current_ms_fragments = [];
                    else:
                        s = s.split(' ');
                        current_ms_fragments[0].append(float(s[0]));
                        current_ms_fragments[1].append(float(s[1]));
                        
                elif s.startswith('RTINSECONDS='):
                    current_rt = float(s.split('=')[1]) / 60.0;

                elif '=' in s:
                    pass

                elif ' ' in s:
                    s = s.split(' ');
                    try:
                        mz = float(s[0]);
                        intens = float(s[1]);
                        reading_peaks = True;
                        current_ms_fragments.append([mz]);
                        current_ms_fragments.append([intens]);
                    except:
                        printlog('%s does not contain proper float pair! Ignoring...'%s);
                    
            elif s.startswith('BEGIN IONS'):
                in_record = True;
                
    
    for i in range(len(ms_fragments)):
        ms_fragments[i] = np.array(ms_fragments[i], dtype = np.float64);
        
    return np.array(rt_peaks, dtype = np.float64), ms_fragments;
        
    
    

def load_nist_fragments(fragfilename):
    rt_peaks = [];
    ms_fragments = [];
    #deconv = [];
    reading_peaks = False;
    n_expected_peaks = 0;
    current_ms_fragments = [];
    with open(fragfilename, 'r') as finp:
        for s in finp:
            s = s.rstrip('\n');
            if reading_peaks:
                s = s.split(';');
                for block in s:
                    if (' ' in block) and reading_peaks:
                        subblocks = block.lstrip().rstrip().split(' ');
                        current_ms_fragments[0].append(float(subblocks[0]));
                        current_ms_fragments[1].append(float(subblocks[1]));
                        if len(current_ms_fragments[0]) >= n_expected_peaks:
                            ms_fragments.append(current_ms_fragments);
                            reading_peaks = False;
                            n_expected_peaks = 0;
                            current_ms_fragments = [];
                            break;
                    elif not reading_peaks:
                        break;
            elif s.startswith('Name:'):
                rt = s[s.index('time_') + 5:s.index('_min')];
                rt_peaks.append(float(rt));
                #if '(dec. ' in s:
                #    dec = s[s.index('(dec.') + 6:];
                #    dec = dec[:dec.index('%')];
                #    deconv.append(float(dec));
                
            elif s.startswith('Num Peaks:'):
                num_p = s[s.index(':') + 1 :];
                reading_peaks = True;
                n_expected_peaks = int(num_p);
                current_ms_fragments.append([]);
                current_ms_fragments.append([]);
        
    
    for i in range(len(ms_fragments)):
        ms_fragments[i] = np.array(ms_fragments[i], dtype = np.float64);
        
    return np.array(rt_peaks, dtype = np.float64), ms_fragments#, np.array(deconv, dtype = np.float64);
        



def reconstruct_datasets(dbfilename, quantity_integrals, fragments, h5writepath, h5fullprofile, delta_mz, delta_rt):

    if len(fragments[0]) != len(quantity_integrals[0]):
        printlog('RT lists between quantity integrals and fragmentation patterns do not match! %s vs %s'%(len(quantity_integrals[0]), len(fragments[0])));
        return
    
    #rts, dataset_names, data_values, mzs, intfrac, deconvoluted
    (rts, dataset_names_list, data_values, imzs, intfrac, deconvoluted) = quantity_integrals;
    
    dd = np.abs(np.subtract(fragments[0], quantity_integrals[0]));
    mask = dd > delta_rt;
    dmismatch = np.sum(mask);
    if dmismatch > 0:
        printlog('RT lists between quantity integrals and fragmentation patterns do not match withing %.3f tolerance!');
        dif1 = fragments[0][mask];
        dif2 = quantity_integrals[0][mask];
        indx = np.arange(1, mask.shape[0] + 1, dtype = np.int64)[mask];
        for i in range(dif1.shape[0]):
            printlog('Mismatch in\t%s:\tQI_RT:\t%.3f\tFP_RT:\t%.3f\tAllowed tolerance:\t%.3f'%(indx[i], dif2[i], dif1[i], delta_rt));
    
    with h5py.File(dbfilename, 'a') as h5file:   
        if h5writepath in h5file:
            work_group = h5file[h5writepath]
        else:
            work_group = h5file.create_group(h5writepath);
    
        crt = fragments[0];
    
        ms_spectra = fragments[1];
    
        mzs = [];
    
        for i in range(len(ms_spectra)):
            mzs.append(ms_spectra[i][0, :])
            
        cmz = np.sort(np.unique(np.hstack(mzs)));
        
        cmz = condense_with_tolerance(cmz, delta_mz);
        
        n_cmz = cmz.shape[0];
        n_crt = crt.shape[0];
        n_samples = data_values.shape[0];
        
        if 'quantity_integrals' in work_group:
            q_i = work_group['quantity_integrals']
            q_i.resize((n_samples, n_crt))
        else:
            q_i = work_group.create_dataset('quantity_integrals', shape = (n_samples, n_crt), maxshape = (n_samples, None),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64)

        q_i[:, :] = data_values[:, :];
                
        if 'integral_MS_spectra' in work_group:
            frag_pattern = work_group['integral_MS_spectra']
            frag_pattern.resize((n_crt, n_cmz))
        else:
            frag_pattern = work_group.create_dataset('integral_MS_spectra', shape = (n_crt,n_cmz), maxshape = (None, n_cmz),
                                                          chunks = True, compression="gzip", 
                                                          compression_opts = 5, dtype = np.float64)

        for i in range(n_crt):
            spec = np.zeros(n_cmz, dtype = np.float64);
            match_ind = nn_match(cmz, fragments[1][i][0, :], tolerance = delta_mz);
            mask = match_ind >= 0;
            spec[mask] = fragments[1][i][1, match_ind[mask]];
            
            max_spec = np.max(spec);
            
            if max_spec > 0.0:
                spec = spec / max_spec;
                
            frag_pattern[i, :] = spec[:];
            
        
        mh5.save_dataset(h5file, h5writepath + '/grouped_rts', crt * 60.0);
        mh5.save_dataset(h5file, h5writepath + '/grouped_cmz', cmz)

        if 'X_3D' in work_group:
            dc_X_3D = work_group['X_3D'];
            dc_X_3D.resize((n_samples, n_cmz, n_crt));
        else:
            dc_X_3D = work_group.create_dataset('X_3D', shape = (n_samples, n_cmz, n_crt), maxshape = (None, None, None),
                                            chunks = True, compression="gzip", 
                                            compression_opts = 5, dtype = np.float64);                                                           

        max_frag = np.sum(frag_pattern, axis = 1);
        
        frag = np.array(frag_pattern);
        
        mask = max_frag > 0.0;
        
        frag[mask, :] = frag[mask, :]/(max_frag[mask].reshape(mask.shape[0], 1));
        
        dc_X_3D[:, :, :] = frag.transpose().reshape((1, n_cmz, n_crt))[:, :, :];
        
        dc_X_3D[:, :, :] = dc_X_3D[:, :, :] * np.array(q_i).reshape((n_samples, 1, n_crt));

        if 'dataset_names' in work_group:
            dataset_names = work_group['dataset_names'];
            dataset_names.resize((n_samples, 2));
        else:
            dataset_names = work_group.create_dataset('dataset_names', shape = (n_samples, 2), 
                                                      chunks = (10000, 2), maxshape=(None, 2), compression="gzip", compression_opts = 5, 
                                                      dtype = np.uint64);
                                                      
                
                
        #utf_8 array to hold strings
        if 'utf_8' in work_group:
            utf_8 = work_group['utf_8'];
        else:
            utf_8 = work_group.create_dataset('utf_8', shape = (1, ), maxshape = (None, ),
                                                      chunks = (100000, ), compression="gzip", 
                                                      compression_opts = 5, dtype = np.uint8);
                                                      
        h5write_strings(dataset_names, utf_8, dataset_names_list, overwrite = True);

        work_group.attrs['deconvoluted'] = deconvoluted;
        work_group.attrs['Imported'] = True;
        
        mh5.save_dataset(h5file, h5writepath + '/group_variance', intfrac);
        
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
                        
        mh5.save_dataset(h5file, h5writepath + '/rel_integrals',\
                                                 data = rel_integral.reshape(q_i.shape), compression_opts = 5)
    
        mh5.save_dataset(h5file, h5writepath + '/order',\
                                                 data = orderall.reshape(q_i.shape), compression_opts = 5)
            
        mean_peak_width = np.median(np.diff(crt));
        print(mean_peak_width)
        
        #work_group.attrs['mean_peak_width'] = mean_peak_width / 4 * 60.0;
        
        for i in range(len(dataset_names_list)):
            dataset_name = dataset_names_list[i];
            mh5.save_dataset(h5file, h5writepath + dataset_name + '/quantity_integrals',\
                                                data = q_i[i, :], compression_opts = 5)
            
            sub_group = work_group[dataset_name];
            sub_group.attrs['deconvoluted'] = deconvoluted;
            sub_group.attrs['has_integrals'] = True;
            sub_group.attrs['re_imported'] = True;
            sub_group.attrs['is_OK'] = True;
            sub_group.attrs['is_processed'] = True;
            sub_group.attrs['is_continuous'] = False;
            sub_group.attrs['is_raw'] = False;
            sub_group.attrs['is_sample_dataset'] = True;
        
        
        #mh5.save_dataset(h5file, h5writepath + '/rel_integrals', relmaxint
        #mh5.save_dataset(h5file, h5writepath + '/grouped_rts', bestorder
    
    
    



def reimport_results(params):
    dbfilename = params['dbfilename'];
    fragfilename = params['fragfilename'];
    ticfilename = params['ticfilename'];
    
    dbfilename = os.path.abspath(dbfilename);
    fragfilename = os.path.abspath(fragfilename);
    ticfilename = os.path.abspath(ticfilename);
    
    if not os.path.isfile(dbfilename):
        printlog('File %s not found! Exiting...'%dbfilename);
        return

    if not os.path.isfile(fragfilename):
        printlog('File %s not found! Exiting...'%fragfilename);
        return

    if not os.path.isfile(ticfilename):
        printlog('File %s not found! Exiting...'%ticfilename);
        return
    
    if os.path.splitext(dbfilename)[1] != '.h5':
        printlog('Unrecognised file extension: %s. Expected ".h5" Exiting...'%dbfilename);
        return

    if os.path.splitext(ticfilename)[1] != '.csv':
        printlog('Unrecognised file extension: %s. Expected ".csv" Exiting...'%ticfilename);
        return

    if (os.path.splitext(fragfilename)[1] != '.mgf') and (os.path.splitext(fragfilename)[1] != '.txt'):
        printlog('Unrecognised file extension: %s. Expected ".txt" or ".mgf" Exiting...'%fragfilename);
        return
        
    quantity_integrals = load_tic_file(ticfilename);

    if quantity_integrals is None:
        printlog('Error! Failed to load csv TIC/EIC table from %s! Terminating...'%ticfilename);
        return


    if (os.path.splitext(fragfilename)[1] == '.mgf'):
        fragments = load_mgf_fragments(fragfilename);
    elif (os.path.splitext(fragfilename)[1] == '.txt'):
        fragments = load_nist_fragments(fragfilename);
    else:
        fragments = None;
       
        
    if fragments is None:
        printlog('Error! Failed to load fragmentation patterns from %s! Terminating...'%fragfilename);
        return
        
    reconstruct_datasets(dbfilename, quantity_integrals, fragments, h5Base.correct_h5path(params['h5writepath']), h5Base.correct_h5path(params['h5fullprofile']),
                         params['dmz'], params['drt']);
    

#Testing:
#i:/FTP/GCMS/testData/Calibration/Results9/Calibration.h5 e:/FTP/GCMS/testData/Calibration/Meta/TIC_original.csv  e:/FTP/GCMS/testData/Calibration/Meta/master_peak_list.txt --h5writepath /re-import_test1
#i:/FTP/GCMS/testData/Calibration/Results7/Calibration.h5 i:/FTP/GCMS/testData/Calibration/Results7/Calibration_integrals.csv  i:/FTP/GCMS/testData/Calibration/Results7/Calibration_ms_peaks.txt --h5writepath /re-import_test1
#i:/FTP/GCMS/MSV000080892/Results_for10_2/GC_data_for_Jamie.h5 e:/FTP/GCMS/MSV000080892/meta/TIC_reformatted_simple.csv e:/FTP/GCMS/MSV000080892/meta/spectra_cheese_stilton_bonde_1706.mgf --h5writepath /re-import_test1

#
#===========================================================================

#Here the main part of the code which is executed when the module is run starts
if __name__ == "__main__": 
    tic(); #Start default timer
    
    #Create command line options handler
    settings = OptionsHolder(__doc__, cmdline_options); 
    
    #Set module short description. <Replace 'Template module' with your description>
    settings.description = 'Template module';
    settings.do = 'yes'   #Legacy. If you do not intend to - just do not run the module
    
    #Print full module description from header. <Can be changed safely to print 
    #instead of printlog since logging is not initialized yet, but kept for consistency>
    printlog(settings.program_description)   
    
    #Parse command line parameters
    try:
        settings.parse_command_line_args()   
    except Exception as inst:
        printlog('!!! Error in command line parameters: !!!');
        printlog(inst);
        printlog('\nRun python ' + sys.argv[0] + ' --help for command line options information!');
        sys.exit(-1)

    #Initialize log file if logfile parameter is set. Overwrite existing logfile
    #if it already exists and overwrite_logfile is set to yes. 
    parameters = settings.parameters;
    if parameters['logfile'] != '':
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'), verbosity_level = parameters['verbose']);
        #Repeat prining of the module description in order to write it to the initialized log file as well.
        #Second printing of the description to the screen is suppressed via print_enabled = False, 
        #only printing to log is enabled.
        printlog(settings.program_description, print_enabled = False);

    #Print when the script has started    
    printlog('Started on %s ...'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));      
    
    #Print values of parameters from command line parsing to be used by the script    
    printlog(settings.format_parameters())   
    
    reimport_results(settings.parameters);
   
    #Finalization stats and timing
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    
    #Print description ending here
    printlog(settings.description_epilog);
    
    #stop logging
    stop_log();



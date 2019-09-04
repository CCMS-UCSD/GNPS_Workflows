# -*- coding: utf-8 -*-
"""

*******************************************************************
Exporting output data module 
*******************************************************************

The module is designed to export results of pre-processing to
CSV and TXT formats.

run python.exe export.py --help to get info about parameters of the script
"""


import os
import time
import sys;
import h5py
import numpy as np
#import bisect


if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

import proc.io.manageh5db as mh5
from proc.procconfig import Exporting_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.h5utils import h5read_strings;
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;
from proc.utils.matching import match_lists, nn_match, condense_with_tolerance;



def export_metadata_table_to_file(dbfilepath, h5readpath, output_prefix, dataset_names, samples):

    printlog('Exporting associated metadata...');
    metacolumns = set();
    
    if not ('*' in samples):
        samples = set(samples);
        dn = [];
        #print(samples)
        #print(dataset_names)
        for dataset_name in dataset_names:
            if dataset_name.lstrip('/') in samples:
                dn.append(dataset_name);
        if not dn:
            printlog('No samples found matching the provided sample list!');
            return
            
        dataset_names = dn;    

    with h5py.File(dbfilepath, 'r') as h5file:

        for dataset_name in dataset_names:
            
            group_name = h5readpath[:-1] + dataset_name;
            group = h5file[group_name];
            if 'MetaData' in group:
                metagroup = group['MetaData'];
                for attribute in metagroup.attrs.keys():
                    metacolumns.add(attribute);
        metacolumns = sorted(list(metacolumns));
        
        if metacolumns:
            with open('%s_metadata.csv'%output_prefix, 'w') as fout:
                fout.write('Sample');
                for s in metacolumns:
                    fout.write(',"%s"'%s);
                fout.write('\n');
                for dataset_name in dataset_names:
                    group_name = h5readpath[:-1] + dataset_name;
                    group = h5file[group_name];
                    fout.write('"%s"'%dataset_name.lstrip('/'));
                    if 'MetaData' in group:
                        metagroup = group['MetaData'];
                        for attribute in metacolumns:
                            if attribute in metagroup.attrs:
                                value = metagroup.attrs[attribute];
                            else:
                                value = '';
                            fout.write(',"%s"'%value);
                        fout.write('\n');
    printlog('Done')


        

def export_ms_peak_list_to_file(dbfilepath, h5readpath, output_prefix, dataset_names, rt_list, rt_tolerance):
    printlog('Exporting MS peak list from [%s]%s to %s_ms_peaks.txt...'%(dbfilepath, h5readpath, output_prefix));
    with h5py.File(dbfilepath, 'r') as h5file:
 
        spectra_set = h5readpath+'integral_MS_spectra';
        if not (spectra_set in h5file):
            printlog('Error! integral_MS_spectra not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        cmz_set = h5readpath+'grouped_cmz';
        if not (cmz_set in h5file):
            printlog('Error! grouped_cmz not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        rts_set = h5readpath+'grouped_rts';
        if not (rts_set in h5file):
            printlog('Error! grouped_rts not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return
            
            
        rel_integral_set = h5readpath+'rel_integrals';
        if not (rel_integral_set in h5file):
            printlog('Error! rel_integrals not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        order_set = h5readpath+'order';
        if not (order_set in h5file):
            printlog('Error! order not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        deconvolved = False;
        
        if 'deconvolved' in h5file[h5readpath].attrs:
            deconvolved = h5file[h5readpath].attrs['deconvolved'];
            
        if deconvolved:
            group_variance_set = h5readpath + 'group_variance';
            if not (group_variance_set in h5file):
                printlog('Error! group_variance not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
                return
                
            group_variance = h5file[group_variance_set];
        
        rel_integrals = h5file[rel_integral_set];
        order = np.array(h5file[order_set]);
        spectra = h5file[spectra_set];    
        cmz = h5file[cmz_set];    
        cmz_count = cmz.shape[0];
        rts = h5file[rts_set];
        rts_count = rts.shape[0];
        
        rts_mask = mh5._get_mask_for_rts(rts, rt_list, rt_tolerance);
        
        max_rel_int = np.max(rel_integrals, axis = 0);
        
        all_order = np.max(order);

        order[order == 0] = all_order + 1;
        
        best_order = np.min(order, axis = 0);
        
        
        
        with open('%s_ms_peaks.txt'%output_prefix, 'w') as fout:
            for i in range(rts_count):
                if not rts_mask[i]:
                    continue
                printlog('RT peak %s of %s'%(i+1, rts_count));
                if deconvolved:
                    fout.write('Name:  peak_%s_ret.time_%.2f_min (dec. %s%%, Max_Rel_integral %9.3f, BestOrder %s of %s).\n'%(i+1, rts[i]/60, int(group_variance[i, 7]), max_rel_int[i], best_order[i], all_order));
                else:
                    fout.write('Name:  peak_%s_ret.time_%.2f_min (Max_Rel_integral %9.3f, BestOrder %s of %s)\n'%(i+1, rts[i]/60, max_rel_int[i], best_order[i], all_order));
                fout.write('DB#:  %s\n'%(i+1));
                peak_count = 0;
                peaks = [];
                max_v = np.max(spectra[i,:]);
                for j in range(cmz_count):
                    value = spectra[i,j];
                    if value>0.0:
                        peak_count += 1;
                        peaks.append('%s %s'%(cmz[j], value/max_v));
                
                fout.write('Num Peaks:  %s\n'%peak_count);
                fout.write('%s\n\n'%('; '.join(peaks)));
            
        printlog('Done')        
        

    
def export_integral_table_to_file(dbfilepath, h5readpath, output_prefix, dataset_names, samples, rt_list, rt_tolerance):
    printlog('Exporting integral table from [%s]%s to %s_integrals.csv...'%(dbfilepath, h5readpath, output_prefix));

    if not ('*' in samples):
        samples = set(samples);
    else:
        samples = [];
    
    #print(samples)    
    #print(dataset_names)
    
    with h5py.File(dbfilepath, 'r') as h5file:

        rts_set = h5readpath+'grouped_rts';
        if not (rts_set in h5file):
            printlog('Error! grouped_rts not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        grouped_dataset_names_set = h5readpath+'dataset_names';
        if not (grouped_dataset_names_set in h5file):
            printlog('Error! dataset_names not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        utf_8_set = h5readpath+'utf_8';
        if not (utf_8_set in h5file):
            printlog('Error! utf_8 not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        quantity_integrals_set = h5readpath+'quantity_integrals';
        if not (quantity_integrals_set in h5file):
            printlog('Error! quantity_integrals not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        rel_integral_set = h5readpath+'rel_integrals';
        if not (rel_integral_set in h5file):
            printlog('Error! rel_integrals not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        order_set = h5readpath+'order';
        if not (order_set in h5file):
            printlog('Error! order not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        
        deconvolved = False;
        
        if 'deconvolved' in h5file[h5readpath].attrs:
            deconvolved = h5file[h5readpath].attrs['deconvolved'];
            
        if deconvolved:
            group_variance_set = h5readpath + 'group_variance';
            if not (group_variance_set in h5file):
                printlog('Error! group_variance not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
                return
                
            group_variance = h5file[group_variance_set];


        rel_integrals = h5file[rel_integral_set];
        order = np.array(h5file[order_set]);

        max_rel_int = np.max(rel_integrals, axis = 0);
        
        all_order = np.max(order);

        order[order == 0] = all_order + 1;
        
        best_order = np.min(order, axis = 0);
        

        rts = h5file[rts_set];
        rts_mask = mh5._get_mask_for_rts(rts, rt_list, rt_tolerance);
        
        grouped_dataset_names = h5file[grouped_dataset_names_set];
        utf_8 = h5file[utf_8_set];
        quantity_integrals = h5file[quantity_integrals_set];
        
        d_names = h5read_strings(grouped_dataset_names, utf_8);
        #print(d_names)
        
        with open('%s_integrals.csv'%output_prefix, 'w') as fout:
            fout.write('RTS:');
            for i in range(len(rts)):
                if not rts_mask[i]:
                    continue
                fout.write(',%.2f'%(rts[i]/60));
                if deconvolved:
                    fout.write(' (%s%%)'%(int(group_variance[i, 7])))
            fout.write('\n');

            fout.write('Rel. Max Integral:');
            for i in range(len(rts)):
                if not rts_mask[i]:
                    continue
                fout.write(',%.3f'%(max_rel_int[i]));
            fout.write('\n');
            
            fout.write('Sample\\Best Order:');
            for i in range(len(rts)):
                if not rts_mask[i]:
                    continue
                fout.write(',%s'%(best_order[i]));
            fout.write('\n');
            
            for i in range(len(d_names)):
                dname = d_names[i];
                if samples:
                    if not (dname in samples):
                        continue
                printlog('Sample %s ...'%dname);
                fout.write('%s'%dname);
                integrals = quantity_integrals[i, :];
                for j in range(integrals.shape[0]):
                    if not rts_mask[j]:
                        continue
                    fout.write(',%s'%integrals[j]);
                fout.write('\n');
            
        printlog('Done')        

'''
def export_all_peaks_to_file(dbfilepath, h5readpath, output_prefix, dataset_names):
    printlog('Exporting all peaks from [%s]%s to %s_all_peaks.csv...'%(dbfilepath, h5readpath, output_prefix));
    with h5py.File(dbfilepath, 'r') as h5file:

        grouped_dataset_names_set = h5readpath+'grouped_dataset_names';
        if not (grouped_dataset_names_set in h5file):
            printlog('Error! grouped_dataset_names not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        utf_8_set = h5readpath+'utf_8';
        if not (utf_8_set in h5file):
            printlog('Error! utf_8 not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        grouped_dataset_names = h5file[grouped_dataset_names_set];
        utf_8 = h5file[utf_8_set];
        
        d_names = h5read_strings(grouped_dataset_names, utf_8);
        
        with open('%s_all_peaks.csv'%output_prefix, 'w') as fout:
            fout.write('dataset,m/z,rt grouped,rt original,integral\n');
            for i in d_names:
                group_set = h5readpath + i + '/grouped_peaks';
                if not (group_set in h5file):
                    printlog('Error! grouped_peaks not found in [%s]%s ! Skipping...'%(dbfilepath, group_set))
                    continue
                group = h5file[group_set];
                for j in range(group.shape[1]):
                    fout.write('"%s",%s,%s,%s,%s\n'%(i, group[3, j], group[1, j], group[6, j], group[0, j]))

            
        printlog('Done')        

        
'''
def do_export(dbfilepath, params = {'h5readpath':'/spproc2D_peakdetect', 
                                    'h5fullprofile':'/spproc2D',
                                    'output_prefix':'%HDF5_file_name%', 
                                    'export_ms_peak_list':'yes',
                                    'export_integral_table':'yes', 
                                    #'export_full_peak_list':'no'
                                    }
                                    ):
    
    """
    Exports processed data to CSV/TXT formats for analysis.
    
    Args:
    
        dbfilepath: a user-specified path to the h5 database file
                    
        params: parameters to be used for export:
            h5readpath - path inside HDF5 to the processed dataset
            output_prefix - prefix to be used for the output files
            export_ms_peak_list - whether to export or not MS peak
                                  lists for NIST
            export_integral_table - whether to export or not the 
                                    chromatographic peak integrals
    """     
    
    params['h5readpath'] = h5Base.correct_h5path(params['h5readpath'])
    params['h5fullprofile'] = h5Base.correct_h5path(params['h5fullprofile'])
    dbfilepath = os.path.abspath(dbfilepath);
    dataset_names = mh5.get_dataset_names(dbfilepath,dataset_names=[],pathinh5 = params['h5readpath'][:-1])
    #print(dataset_names)
    if not dataset_names:
        printlog('No datasets found in the h5readpath provided: %s !'%params['h5readpath']);
        return
    
    output_prefix = params['output_prefix'];
    if '%HDF5_file_name%' in output_prefix:
        fname = os.path.splitext(os.path.basename(dbfilepath))[0];
        output_prefix = output_prefix.replace('%HDF5_file_name%',fname);
        
    export_path = params['exportpath'];
    if export_path != '':
        export_path = os.path.abspath(export_path);
    else:
        export_path = os.path.split(dbfilepath)[0];
    
    output_prefix = os.path.join(export_path, output_prefix);
    
    fpath = os.path.split(output_prefix)[0];
    
    if not os.path.exists(fpath):
        os.makedirs(fpath);
        
    if not ('no' in params['export_ms_peak_list']):
        export_ms_peak_list_to_file(dbfilepath, params['h5readpath'], output_prefix, dataset_names, params['rts'], params['rt_tolerance']);

    if not ('no' in params['export_integral_table']):
        export_integral_table_to_file(dbfilepath, params['h5readpath'], output_prefix, dataset_names, params['samples'], params['rts'], params['rt_tolerance']);

    if not ('no' in params['export_metadata_table']):
        export_metadata_table_to_file(dbfilepath, params['h5readpath'], output_prefix, dataset_names, params['samples']);

    '''if not ('no' in params['export_all_peaks']):
        export_all_peaks_to_file(dbfilepath, params['h5readpath'], output_prefix, dataset_names);
    '''                
    return
      
        

if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, Exporting_options);
    settings.description='Exporting processed data';
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
    printlog(settings.format_parameters())   
    
    do_export(settings.parameters['dbfilename'],
                     params = settings.parameters['params'])
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();
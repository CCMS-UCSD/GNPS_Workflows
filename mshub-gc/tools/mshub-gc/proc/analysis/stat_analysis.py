# -*- coding: utf-8 -*-
"""
*******************************************************************
Statistical analysis module for biomarker detection etc.
*******************************************************************

This module is a "gateway" into statistical analysis of the data
in respect to the available metadata. 

The main purpose of this module is biomarker discovery via
such methods as ANOVA, Generalized linear mixed effect models etc.

Analysis is performed per component (i.e. per RT peak corresponding to
an independent compound).


run python.exe stat_analysis.py --help to get info about parameters of the script




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
from proc.procconfig import Stat_analysis_options as cmdline_options;

#Manager for command line options
from proc.utils.cmdline import OptionsHolder

#Timing functions for standard stats output
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log, LoggingException;
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.analysis.methods.methods_list import available_stat_analysis_methods;
from proc.analysis.models.stat_model import StatisticalModel;

import proc.io.manageh5db as mh5




#==========================================================================
#From here the main code starts




def perform_statistical_analysis(method,
                                 methodparams, 
                                 model, 
                                 groupingparams,
                                 samples, 
                                 rts,
                                 rt_tolerance,
                                 output_prefix,
                                 h5readpath,
                                 h5writepath,
                                 exportpath,
                                 dbfilename):
    """
    Core function. Performs statistical analysis using provided method and model.
    Args: method (str)- name of the method to be used, should match one of the methods
                    registered in available_stat_analysis_methods 
                    from proc.analysis.methods.methods_list
          methodparams - corresponding method's parameters as dictionary
          model - string representation of the statistical model to be used.
                  Follows R notation, e.g. 'C(dose)*C(drugtype)'.
          groupingparams - parameters related to grouping of results (dict) by
                  KMeans method from sklearn.cluster,
                  such as group_by, group_weights, n_groups. group_by lists
                  groups of returned values from stat. analysis method to be used
                  for grouping, e.g. 'F' or 'p_value_pass'. group_weights assigns
                  weights to the corresponding groups in group_by list. Default: 
                  1.0. n_groups - number of clusters/groups for the KMeans grouping
                  of results. 
         samples - list of masks for sample names to be included in analysis. 
                 Supports '*' for any number of symbols, '?' for single unknown symbol.
                 Example: '*Hello' will select any sample containing 'Hello' 
                 at the end of its name.
         rts -  list of retention time ranges (min). Every entry can be a number or a 
                 range of boundary values, e.g. '2, 3-8, 20-*'. '*' indicates any value
                 to the end of the existing range. 
        rt_tolerance - select rts within this tolerance from the rts supplied values.
        output_prefix - prefix to be used for the output files. If it contains
                    substring '%HDF5_file_name%', this substring is replaced with 
                    the dbfilename.
        h5readpath - path in hdf5 file to read the data from. If not absolute, 
                    it is assumed to be from the root level.
        h5writepath - path in hdf5 file to write the results to. If not absolute, 
                    it is assumed to be from the root level.
                    
        exportpath - folder to write reports and export results to.
        dbfilename - name (and path) of the hdf5 file with data to be analysed.


    """                                 
                                     
    #Make read and write paths absolute for consistency.
    h5readpath = mh5.abs_hdf5_path(h5readpath); 
    h5writepath = mh5.abs_hdf5_path(h5writepath);
    
    #Get absolute path to the hdf5 file.
    dbfilename = os.path.abspath(dbfilename);
    
    with h5py.File(dbfilename, 'a') as h5file:
        #Get datasets from hdf5 file which contain processed data and metadata
        #Also return their respective indeces in the data array in case alphabetic
        #order was not preserved in previous processing steps. 
        dataset_names, dataset_indexes = mh5.get_dataset_names_from_hdf5(h5file, 
                                                               h5readpath, 
                                                               filter_by_names = samples, 
                                                               filter_by_attributes = {
                                                                   'is_OK':True,
                                                                   'has_integrals':True,
                                                                   'has_metadata':True,
                                                                   'is_processed':True,
                                                                   'is_continuous':False,
                                                                   'is_raw':False,
                                                               }, 
                                                               return_indeces = True);
        if not dataset_names:
            printlog('No datasets matching criteria found in the h5readpath provided: %s !'%h5readpath);
            return

        #Get the list of indeces of rt peaks according to rts selections and rt_tolerance        
        rt_indeces = mh5.get_processed_rt_indeces(h5file, h5readpath, rts, rt_tolerance);
        if len(rt_indeces) == 0:
            printlog('No retention time indeces matching criteria found in the h5readpath provided: %s !'%h5readpath);
            return
            
        #Update output_prefix to contain hdf5 name if its mask is supplied.
        if '%HDF5_file_name%' in output_prefix:
            fname = os.path.splitext(os.path.basename(dbfilename))[0];
            output_prefix = output_prefix.replace('%HDF5_file_name%', fname);
            
        #prepare export_path to be absolute
        #if not supplied - use the path of hdf5 file.
        export_path = params['exportpath'];
        if export_path != '':
            export_path = os.path.abspath(export_path);
        else:
            export_path = os.path.split(dbfilename)[0];
        
        #Get full output_prefix (include absolute path)        
        output_prefix = os.path.join(export_path, output_prefix);
        
        #Make sure the path exists by creating the folder structure if necessary                
        fpath = os.path.split(output_prefix)[0];
        if not os.path.exists(fpath):
            os.makedirs(fpath);
    
        #Instantiate and initialize the statistical model
        stat_model = StatisticalModel(model, groupingparams, h5file, h5readpath, h5writepath, dataset_names, dataset_indexes, rt_indeces, fpath, output_prefix);
        
        #Do the analysis using supplied method and methodparams. For now please
        #call it only once per instance of stat_model created to avoid unexpected
        #behaviour.          
        stat_model.analyse_by_method(method, methodparams);
        
        
    
    
    
    
    

#===========================================================================

#Here the main part of the code which is executed when the module is run starts
if __name__ == "__main__": 
    tic(); #Start default timer
    
    #Create command line options handler
    settings = OptionsHolder(__doc__, cmdline_options); 
    
    #Set module short description. <Replace 'Template module' with your description>
    settings.description = 'Statistical Analysis Module';
    settings.do = 'yes'   #Legacy. If you do not intend to - just do not run the module
    
    printlog(settings.program_description)   
    
    #Parse command line parameters
    settings.parse_command_line_args()   

    #Initialize log file if logfile parameter is set. Overwrite existing logfile
    #if it already exists and overwrite_logfile is set to yes. 
    parameters = settings.parameters;
    if parameters['logfile'] != '':
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'), verbosity_level = parameters['verbose']);
        printlog(settings.program_description, print_enabled = False);

    #Print when the script has started    
    printlog('Started on %s ...'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));      
    
    #Print values of parameters from command line parsing to be used by the script    
    printlog(settings.format_parameters())   
    
    params = parameters['params'];
    methodparams = parameters['methodparams'];
    groupingparams = parameters['grouping'];
    
    perform_statistical_analysis(params['method'],
                                 methodparams,
                                 params['model'], 
                                 groupingparams,
                                 params['samples'], 
                                 params['rts'],
                                 params['rt_tolerance'],
                                 params['output_prefix'],
                                 params['h5readpath'],
                                 params['h5writepath'],
                                 params['exportpath'],
                                 parameters['dbfilename']

                                 );
    
    
                   
   
    #Finalization stats and timing
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    
    #Print description ending here
    printlog(settings.description_epilog);
    
    #stop logging
    stop_log();



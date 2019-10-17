# -*- coding: utf-8 -*-
"""

***********************************************
Preprocessing workflow object management module
***********************************************

The modules includes class for creation and management of pre-processing 
workflow objects to ensure that all passed user parameters are sound.
 
"""

#===========================Import section=================================

#Importing standard and external modules
import os
import sys

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.utils.cmdline import Option, Value, AllValues, PathExists, GreaterOrEqual;
from proc.analysis.methods.methods_list import procconfig_options_for_methods;

#==========================================================================

#Settings for the command line interfaces for different modules

#Common reference set options for processing.
#TODO: test/train set handling
reference_set_options = [                   
                    Option('--refh5path', help = 'The path in HDF5 database for reference(training) data and processing parameters.', values=['/sp2D',None], type=str, level = 1),
                    Option('--refdbfilename', help =  'Reference HDF5 database file with trainig dataset and processing parameters.', values=['', None], type=str, level = 1)
                    ]
                    
#Common logfile options - set for all modules                    
logfile_options = [Option('--logfile', help = 'The file name to which to write the log.', values=['', None], type=str, level = 0),
                   Option('--overwrite_logfile', help = 'Overwrite existing log or not.', values=['no', 'yes'], type=str, level = 0),
                   Option('--verbose', help = 'Overwrite existing log or not.', values=[0, 1, 2, None], type=int, level = 0), #Level of verbosity
                   ];



"""

These options are the template for a typical module. For details on how to 
define all parameters for them for the command line parser - see corresponding 
module documentation for cmdline.py in utils.

In brief, you need to define a list of instances of class Option. Each instance 
is one defined command line option. 

Instances are initialized as follows with defaults indicated:

Option(option, help = '', values = [None], is_list = False, type = None, conditions = [], targets = [], optional = True, level = 0)

with parameters:

1) option: defines the name of the option and how it is presented at the command 
line. Compulsory. Type: str. Option names follow normal python variable name
requirements, i.e. alpha-numeric and underscore allowed. If prefixed with '-' -
it is a named argument and can be positioned anywhere in the command line parameters,
while not prefixed options are positional and should be supplied in the order defined 
in the list. Single '-' in front of single letter indicates a short version of the option, 
'--' indicates full option name, both can be supplied if separated by coma. 
Full version is compulsory, short version is optional.

Example:
    '--h5readpath' - option with full name 'h5readpath'. This is the only form 
    accepted. In the command line it should be supplied as 
    --h5readpath "/some/path".
    
    '-r,--h5readpath' - option 'h5readpath' is defined by both short and full 
    versions. In the command line it can be supplied as either
    -r "/some/path"
    or
    --h5readpath "/some/path"
    
    'dbfilename' - positional argument option, it will be named dbfilename 
    internally, but supplied in the command line according to its sequence order
    in the list of positional argument options.
    
2) help = '': help string describing option. Used to construct automatic help

3) values = [None]: List of allowed values. First value in the list is used as
    default if option is not specified in the parsed command line. If None is
    present in the list - any value is accepted for the option - otherwise only
    the values from this supplied list are accepted. If values is set to None,
    the option is considered a flag switch and does not expect a value to be 
    supplied after it in the command line. In this case its value is set to True
    if this option was supplied in the command line and False otherwise.

4) is_list = False: expect multiple values supplied as coma-separated list in
    the command line. Otherwise only one value is taken.

5) type = None: if not None - the input values are checked and converted to the 
    type specified. E.g. type = str will convert the value to string, type = int 
    to integer value etc.

6) conditions = []: Set of conditions for the entered values to be checked against
    during parsing.

7) targets = []: If provided - overrides the default hierarchial parameters 
    structure to which the output option value is sent. Useful if different 
    selected values of the option would change the default values of other
    global options. This is more advanced topic and is not discussed in detail 
    here.

8) optional = True: Whether this option can be omitted in the command line or
    it should always be provided.

9) level = 0: Level of this option for HTML parameter tree generation. level 0
    options are shown to all users, level 1 - only to advanced ones. Not used 
    in basic command line argument parsing     


When the command line arguments are parsed by OptionsHolder instance method
parse_command_line_args(), they are stored in the parameters variable of this 
instance. Parameters is a dictionary with options as keys and their values 
assigned as values. 

Example: 

for command line options [Option('--h5readpath'), Option('dbfilename')]

and command line: python <yourmodule>.py --h5readpath "/subpath1" "/db1.fname"
you will have 
parameters = {"h5readpath":"/subpath1", "dbfilename":"/db1.fname"};
in your instance of OptionsHolder.


You may have a hierarchial form of options where subsequent options are defined
depending upon the parent option value provided. This is a more complex case
and is described in detail in the documentation for cmdline.py. 
In brief, if you have the option which value selection defines which other options
are becoming relevant - you can supply its possible values in the values = []
list using Value instances. In this case only Value instances will be allowed in 
values list and no None is allowed there.

Each Value(value, help='', parameters=[]) instance is initiated with:
value: option value 
help: help line describing this particular pre-selectable value for the parent 
    option
parameters: list of Option instances which are dependent upon the selection
    of this particular value. 
    
By default sub-options values are placed in parameters in
"parentoption_parentoptionvalue", but if their targets list is populated,
they are redirected into the structure provided by the string in the targets list.
This way you can change the default values for Options which depend upon the 
pre-selection of other Options values. This is recursive procedure, so in theory
any level of complexion is achieveable. 
See details in the cmdline.py documentation.
    
"""

Template_options = [
                   #Modules often require input path in HDF5 file for input data and output path in HDF5 file for results:
                    Option('--h5readpath', help = 'The path in HDF5 database for reading the data from.', values=['/source_data_path', None], type=str, level = 0),
                    Option('--h5writepath', help = 'The path in HDF5 database for writing data.', values=['/processed_data_path', None], type=str, level = 0),
                    
                    ] + logfile_options + [ #Log file optins added
                    
                   #Modules usually operate on the HDF5 file: 
                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),

                    ];

#Raw file format importer settings
ImportSet_options=[Option('-f,--filetype', help = 'Input File Format.', values=[\
                        #Value('*', help = 'Any supported Format', parameters=[\
                        #    Option('--fileext', help = 'Set input file extension.', values=['.*', None], type=str, targets=['/filereadinfo'], level = 0),
                        #    ]),
                        Value('netcdf', help = 'NETCDF File Format', parameters=[\
                            Option('--fileext', help = 'Set input file extension.', values=['.cdf', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--massid', help = 'Set input file identifier for reading mass values.', values=['mass_values', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--specid', help = 'Set input file identifier for reading intensity values.', values=['intensity_values', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--scanid', help = 'Set input file identifier for reading scan acquisition time values.', values=['scan_index', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--timeid', help = 'Set input file identifier for reading scan acquisition scan index values.', values=['scan_acquisition_time', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--timeunits', help = 'Set time units used for retention time.', values=['sec', 'min'], type=str, targets=['/filereadinfo'], level = 0),
                            ]),#,
                        
                        Value('mzml', help = 'mzML File Format', parameters=[\
                            Option('--fileext', help = 'Set input file extension.', values=['.mzml', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--timeunits', help = 'Set time units used for retention time.', values=['min', 'sec'], type=str, targets=['/filereadinfo'], level = 0),
                            ]),

                        Value('mzxml', help = 'mzXML File Format', parameters=[\
                            Option('--fileext', help = 'Set input file extension.', values=['.mzxml', None], type=str, targets=['/filereadinfo'], level = 0),
                            Option('--timeunits', help = 'Set time units used for retention time.', values=['min', 'sec'], type=str, targets=['/filereadinfo'], level = 0),
                            ]),
                        

						], type=str, level = 0),\
                   
                   ] + logfile_options + [ 

                   Option('datapath', help = 'Sets data directory path.', values=[os.getcwd(), None], type=str, conditions=[PathExists('Path must exist!')], level = 0),
                   Option('dbfilename', help = 'Output HDF5 file name.', values=['', None], type=str, level = 0),
                   ];

#Metadata importer settings
ImportMetaSet_options=[Option('-f,--filetype', help = 'Input File Format.', values=[
                        Value('csv', help = 'Comma separated values table')#,
                        ], type=str, level = 0),\

                   Option('--h5writepath', help = 'The path in HDF5 database for writing data.', values=['/sp2D', None], type=str, level = 0),
                   Option('--overwrite', help = 'Overwrite existing metadata.', values=['yes', 'no'], type=str, level = 0),  
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('metafilename', help =  'File with metadata.', values=['', None], type=str, optional=False, level = 0),
                   ];

#HDF5 manipulator module settings
Manipulate_options=[
                   Option('--h5path', help = 'The path in HDF5 to set as current.', values=['/', None], type=str, level = 0),

                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('commandfilename', help =  'Text file with commands to be executed. If not supplied, the script will start in interactive mode.', 
                          values=['', None], type=str, optional=True, level = 0),
                   ];

#Data exporting module settings
Exporting_options=[
                   Option('--export_integral_table', help = 'Export peak integrals to CSV table.', values=['yes', 'no'], type = str, targets=['/params'], level = 0),  
                   Option('--export_ms_peak_list', help = 'Export MS peaks in TXT for NIST.', values=['yes', 'no'], type = str, targets=['/params'], level = 0),  
                   Option('--export_metadata_table', help = 'Export metadata available for samples.', values=['yes', 'no'], type = str, targets=['/params'], level = 0),  
                   Option('--samples', help = 'Coma separated selection of samples to be exported.', values=['*', None], is_list = True, type = str, targets=['/params'], level = 0),   
                   Option('--rts', help = 'Coma separated selection of retention time peaks or ranges to be exported.', values=['*', None], is_list = True, type = str, targets=['/params'], level = 0),   

                   Option('--rt_tolerance', help = 'Tolerance for RT peak matching, min.', values=[0.1, None], type = float, targets=['/params'], level = 0),   

                   #Option('--export_all_peaks', help = 'Export all peaks to CSV table.', values=['yes', 'no'], type=str, targets=['/params'], level = 0),  
                   Option('--output_prefix', help = 'Prefix to be added to output file names.', values=['%HDF5_file_name%', 'export', 'output', 'results', '', None], type=str, targets=['/params'], level = 0),  
                   Option('--h5readpath', help = 'The path in HDF5 database for reading data.', values=['/spal2D_peakdetect',None], type=str, targets=['/params'], level = 1), 
                   Option('--h5fullprofile', help = 'The path in HDF5 database for the full profile dataset.', values=['/spal2D',None], type=str, targets=['/params'], level = 1), 
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('exportpath', help =  'Output path for export.', values=['', None], type=str, targets=['/params'], optional=True, level = 0),
                   ];



ReImport_Results_options = [
                   Option('--h5writepath', help = 'The path in HDF5 database for writing data.', values=['/re_imported', None], type=str, level = 0),
                   Option('--h5fullprofile', help = 'The path in HDF5 database for the full profile reference dataset.', values=['/spal2D', None], type=str, level = 1), 
                   Option('--dmz', help = 'M/Z tolerance. Da.', values=[0.3, None], type=float, level = 1), 
                   Option('--drt', help = 'Retention time tolerance. Min.', values=[0.1, None], type=float, level = 1),   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5 database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('ticfilename', help =  'TIC/EIC in *.csv table format.', values=['', None], type=str, optional=False, level = 0),
                   Option('fragfilename', help =  'MS fragmentation patterns in NIST (*.txt) or GNPS (*.mgf) format.', values=['', None], type=str, optional=False, level = 0),
                   
                   ];

#Individual sample plots generator
Plot_samples_options = [
                   Option('--plot_width', help = 'Bokeh plots default width (pixels).', values=[1100, None], type=int, targets=['/params'], level = 1),  
                   Option('--top_plot_height', help = 'Bokeh top plots default height (pixels).', values=[250, None], type=int, targets=['/params'], level = 1),  
                   Option('--bottom_plot_height', help = 'Bokeh bottom plots default height (pixels).', values=[400, None], type=int, targets=['/params'], level = 1),  
                   Option('--global_maximum', help = 'Normalize all plots to global maximum.', values=['yes', 'no'], type=str, targets=['/params'], level = 0),  
                   Option('--output_prefix', help = 'Prefix to be added to output file names.', values=['%HDF5_file_name%', 'export', 'output', 'results', '', None], type=str, targets=['/params'], level = 0),  

                   Option('--h5readpath', help = 'The path in HDF5 database for reading data.', values=['/spal2D',None], type=str, targets=['/params'], level = 1), 
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('exportpath', help =  'Output path for export.', values=['', None], type=str, targets=['/params'], optional=True, level = 0),
                   ];

#HTML report generator settings
Reporting_options=[
                   Option('--plot_width', help = 'Bokeh plots default width (pixels).', values=[1100, None], type=int, targets=['/params'], level = 1),  
                   Option('--top_plot_height', help = 'Bokeh top plots default height (pixels).', values=[250, None], type=int, targets=['/params'], level = 1),  
                   Option('--bottom_plot_height', help = 'Bokeh bottom plots default height (pixels).', values=[400, None], type=int, targets=['/params'], level = 1),  
                    
                   Option('--output_prefix', help = 'Prefix to be added to output file names.', values=['%HDF5_file_name%', 'export', 'output', 'results', '', None], type=str, targets=['/params'], level = 0),  

                   Option('--h5readpath', help = 'The path in HDF5 database for reading data.', values=['/spal2D_peakdetect',None], type=str, targets=['/params'], level = 1), 
                   Option('--h5fullprofile', help = 'The path in HDF5 database for the full profile dataset.', values=['/spal2D',None], type=str, targets=['/params'], level = 1), 
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('exportpath', help =  'Output path for export.', values=['', None], type=str, targets=['/params'], optional=True, level = 0),
                   ];

#Intra peak alignment settings
IntraPAlign_options=[\

                   Option('--method', help = 'Peak alignment method.', values=[
                        Value('binning', help = 'm/z binning', parameters=[
                            Option('--units', help = 'm/z units', values=['Da'], type=str, targets=['/params'], level = 0),
                            Option('--binsize', help = 'Bin size', values=[1, None], type=float,
                                   conditions=[GreaterOrEqual('binsize>=0.0', 0.0)], targets=['/params'], level = 1),
                            Option('--binshift', help = 'Bin boundary shift', values=[0.3, None],
                                   type=float, conditions=[GreaterOrEqual('binshift>=0.0', 0.0)], targets=['/params'], level = 1),
                            ])
                        ], type=str, level = 0),
                   Option('--h5writepath', help = 'The path in HDF5 database for writing data.', values=['/sp2D',None], type=str, targets=['/params'], level = 1),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [
                   
                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0)
                   
                   ];

#Inter-sample profile alignment settings
ProfAlign_options=[\

                   Option('--method', help = 'Inter-sample profile alignment method.', values=[
                        Value('rspa', help = 'Recursive Segment-wise Peak Alignment', parameters=[
                            Option('--reference', help = 'Options for profile reference.', values=['mean','median'], type=str, targets=['/params'], level = 0),
                            Option('--minsegwidth', help = 'Minimum segment width.', values=['auto', 100, None], type=str, #?10pw
                                   #conditions=[GreaterOrEqual('minsegwidth>=0.0', 0.0)], 
                                               targets=['/params'], level = 0),
                            Option('--maxpeakshift', help = 'Maximum allowed peak shift (in seconds).', values=['auto', 10, None], # ?5pw
                                   type=str, 
                                   #conditions=[GreaterOrEqual('maxpeakshift>=0.0', 0.0)], 
                                               targets=['/params'], level = 0),
                            Option('--recursion', help = 'The local and global alignment is performed if true.', values=[1,0],
                                   type=float, targets=['/params'], level = 0),
                            ])
                        ], type=str, level = 0),
                   Option('--h5readpath', help = 'The path for reading data from HDF5 database.', values=['/spproc2D',None], type=str, targets=['/params'], level = 0),
                   Option('--h5writepath', help = 'The path for writing data to HDF5 database.', values=['/spproc2D',None], type=str, targets=['/params'], level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0)
                   ];


InternalAlign_options=[\

                   Option('--method', help = 'Intra-sample profile alignment method.', values=[
                        Value('rspa', help = 'Recursive Segment-wise Peak Alignment', parameters=[
                            Option('--reference', help = 'Options for profile reference.', values=['mean','median'], type=str, targets=['/params'], level = 0),
                            Option('--minsegwidth', help = 'Minimum segment width.', values=['auto', 100, None], type=str, #?10pw
                                   #conditions=[GreaterOrEqual('minsegwidth>=0.0', 0.0)], 
                                               targets=['/params'], level = 0),
                            Option('--maxpeakshift', help = 'Maximum allowed peak shift (in seconds).', values=['auto', 10, None], # ?2pw
                                   type=str, 
                                   #conditions=[GreaterOrEqual('maxpeakshift>=0.0', 0.0)], 
                                               targets=['/params'], level = 0),
                            
                            Option('--recursion', help = 'The local and global alignment is performed if true.', values=[1, 0],
                                   type=float, targets=['/params'], level = 0),
                            ])
                        ], type=str, level = 0),
                   Option('--h5readpath', help = 'The path for reading data from HDF5 database.', values=['/spproc2D',None], type=str, targets=['/params'], level = 0),
                   Option('--h5writepath', help = 'The path for writing data to HDF5 database.', values=['/spproc2D',None], type=str, targets=['/params'], level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0)
                   ];


#VisTic module visualization of the continuous profile alignments in Bokeh settings
TICvis_options=[\
                   Option('--plot_width', help = 'Bokeh plots default width (pixels).', values=[1100, None], type=int, targets=['/params'], level = 1),  
                   Option('--plot_height', help = 'Bokeh top plots default height (pixels).', values=[900, None], type=int, targets=['/params'], level = 1),                     
                   Option('--display', help = 'Open generated plot in default browser.', values=['no', 'yes'], type=str, targets=['/params'], level = 1),                     

                   Option('-m,--method', help = 'Visualization of Total Ion Chromatogram(s).', values=[
                        Value('bokeh', help = '2D plots', parameters=[
                            Option('--outputfile', help = 'Output data file.', values=['',None], type=str, targets=['/params'], level = 0),
                            #Option('--inline', help = 'Display plots inline.', values=None, type=str, targets=['/params'], level = 0),
                            ]),\
                        #Value('pyplot', help = '2D plots', parameters=[
                        #    Option('--inline', help = 'Display plots inline.', values=None, type=str, targets=['/params'], level = 0),
                        #    ]),
                        ], type=str, level = 0),
                   Option('--h5readpath', help = 'The path for reading data fron HDF5 database.', values=['/sp2D',None], type=str, targets=['/params'], level = 0),

                   ] + logfile_options + [
                   
                   Option('dbfilename', help = 'HDF5  database file with deposited multiple MS datasets.', is_list=False, values=['', None], type=str, optional=False, level = 0)
                   ]; 
 
#Noise filtering module settings
NoiseFilter_options=[\

                   Option('--smoothmethod', help = 'Noise filtering method.', values=[
                        Value('sqfilter', help = 'The Savitzky-Golay filter', parameters=[
                            Option('--window', help = 'Window size in seconds (~ equal to the width of average peak).', values=['auto', 2.5, None],#pw*0.5
                                   type=str,# conditions=[GreaterOrEqual('window>=0.0', 0.0)], 
                                              targets=['/smoothparams'], level = 0),
                            Option('--degree', help = 'Polynomial degree', values=[3, None], type=float,
                                   conditions=[GreaterOrEqual('degree>=0.0', 0.0)], targets=['/smoothparams'], level = 0),
                            ]),
                        Value('none', help = 'Do not perform intensity smoothing', parameters=[
                            #Option('--no_noise', help = 'No noise removal', values=['', None], type=str, targets=['/smoothparams'], level = 0), #Remove this
                            ]),
                        ], type=str, level = 0),

                   Option('--baselinemethod', help = 'Baseline correction method.', values=[
                        Value('tophat', help = 'top-hat morphological filter for baseline correction', parameters=[
                            Option('--frame', help = 'Frame size in secs (~ equal to the timeframe of 15 peaks).', values=['auto', 90, None], #15pw
                                   type=str, #conditions=[GreaterOrEqual('frame>=0.0', 0.0)], 
                                                           targets=['/baselineparams'], level = 0),
                            ]),
                        Value('none', help = 'Do not perform baseline correction', parameters=[
                            Option('--no_baseline', help = 'No baseline', values=['', None], type=str, targets=['/baselineparams'], level = 0), #Remove this
                            ]),
                        ], type=str, level = 0),
                   Option('--h5readpath', help = 'The path for reading data from HDF5 database.', values=['/sp2D',None], type=str, targets=['/params'], level = 0),
                   Option('--h5writepath', help = 'The path for writing data into HDF5 database.', values=['/spproc2D',None], type=str, targets=['/params'], level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('dbfilename', help = 'HDF5  database file with deposited multiple MS datasets.', is_list=False, values=['', None], type=str, optional=False, level = 0)
                   ]; 


#Peak detection module settings
PeakDetection_options=[\

                   Option('--peak_detect_method', help = 'Peak detection method.', values=[
                        Value('smoothderiv', help = 'The peak detection method based on zero crossing of the smoothed derivative signal', parameters=[
                            
                            Option('--min_width', help = 'The expected width of the smallest peak or the minimum gap between peaks.', values=['auto', 3, None],#pw*0.3
                                   type=str, #conditions=[GreaterOrEqual('min_width>=0.0', 0.0)], 
                                                           targets=['/peak_detect_params'], level = 0),
                            
                            Option('--local_baseline_correction', help = 'Correct peak integrals according to local baseline linear interpolation.', values=None,
                                   targets=['/peak_detect_params'], level = 0),

                            ])
                        ], type=str),

                   Option('--global', help = 'The global threshold applied to all samples if set to yes', values=['no','yes'], type=str,  targets=['/peak_filter_params'],level = 0), 
                   
                   Option('--peak_filter_method', help = 'Peak filtering method for per-sample filtering.', values=[
                        Value('slope', help = 'The peak filtering using slope assessment', parameters=[
                            Option('--int_thr', help = 'Peak intensity threshold.', values=['auto', None], type=str, targets=['/peak_filter_params'], level = 0),
                            Option('--left_ang_thr', help = 'Left peak angular(slope) threshold.', values=['auto', None], type=str, targets=['/peak_filter_params'], level = 0),
                            Option('--right_ang_thr', help = 'Right peak angular(slope) threshold.', values=['auto', None], type=str, targets=['/peak_filter_params'], level = 0),
                            ])
                        ], type=str, level = 0),
                        
                            
                   Option('--peak_group_method', help = 'Peak grouping method.', values=[
                        Value('kernel', help = 'The peak grouping method is based on the weighted sum of retention time values', parameters=[
                            Option('--weighted_density', help = 'Histogram weighted by peak intensity for chromatographic peak clustering.', values=['no', 'yes'], type=str, targets=['/peak_group_params'], level = 0),
                            Option('--rt_tol', help = 'Retention time tolerance.', values=['auto', None], type=str, targets=['/peak_group_params'], level = 0), #pw*0.5
                            #TODO: if aligned 0.25 pw, if not - more
                            ])
                        ], type=str, level = 0),
                   
                   Option('--individual', help = 'Treat samples individually or together. (Ignored if deconvolution enabled).', values=['no', 'yes'], type=str, targets=['/peak_group_params'], level = 0),
                   
                   Option('--frag_pattern', help = 'Fragmentation pattern extractor.', values=['deconvolution', 'max', 'aggregate'], type=str, targets=['/peak_group_params'], level = 0),
                   Option('--occurence', help = 'Peak integral caclulator based on all or the most common ionic species.', values=['common', 'all'], type=str, targets=['/peak_group_params'], level = 0),
                               
                   
                   Option('--h5readpath', help = 'The path for reading data from HDF5 database.', values=['/spal2D',None], type=str, level = 0),
                   Option('--h5writepath', help = 'The path for writing data to HDF5 database.', values=['/spal2D_peakdetect',None], type=str, level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], 
                          type=str, optional=False, level = 0)
                   ];


#Intra-sample normalization settings
IntraNorm_options=[\
                   Option('--method', help = 'Intranormalization method.', values=[
                        Value('mfc', help = 'Median fold change', parameters=[
                            Option('--reference', help = 'Refence dataset with respect to which the fold intensity changes of other datasets are calculated.', 
                                values=['mean'], type=str, targets=['/params'], level = 0),
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, targets=['/params'], level = 0),
                            ]),

                        Value('mean', help = 'Mean', parameters=[
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, targets=['/params'], level = 0),
                            ]),
                        
                        Value('median', help = 'Median', parameters=[
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, targets=['/params'], level = 0),
                            ])
                        ], type=str),
                   Option('--min_mz', help = 'Lower limit for M/Z values.', values=[0.0, None], type=float, conditions=[GreaterOrEqual('min_mz>=0.0', 0.0)], level = 0),
                   Option('--max_mz', help = 'Upper limit for M/Z values.', values=[50000.0, None],  type=float, conditions=[GreaterOrEqual('max_mz>=0.0', 0.0)], level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [
                   
                   Option('h5dbname', help = 'Input HDF5 file name(s).', is_list=False, values=['', None], type=str, optional=False, level = 0)                   
                   ]; #end of value IntraNorm

#Intersample normalization module settings
InterNorm_options=[\
                   Option('--method', help = 'Inter-normalization method.', values=[
                        Value('mfc', help = 'Median fold change', parameters=[
                            Option('--reference', help = 'Refence dataset with respect to which the fold intensity changes of other datasets are calculated.', 
                                values=['mean'], type=str, targets=['/params'], level = 0),
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0.0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, targets=['/params'], level = 0),
                            ]),

                        Value('mean', help = 'Mean', parameters=[
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0.0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, type=str, targets=['/params'], level = 0),
                            ]),
                        
                        Value('median', help = 'Median', parameters=[
                            Option('--offset', help = 'Disregard peak intensity smaller that this value.', 
                                values=[0.0, None], type=float, conditions=[GreaterOrEqual('offset>=0.0', 0.0)], targets=['/params'], level = 0),
                            Option('--outliers', help = 'Outliers.', 
                                values=None, type=str, targets=['/params'], level = 0),
                            ])
                        ], type=str, level = 0),
                   Option('--min_mz', help = 'Lower limit for M/Z values.', values=[0.0, None], type=float, conditions=[GreaterOrEqual('min_mz>=0.0', 0.0)], level = 0),
                   Option('--max_mz', help = 'Upper limit for M/Z values.', values=[50000.0, None],  type=float, conditions=[GreaterOrEqual('max_mz>=0.0', 0.0)], level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [
                   
                   Option('h5dbname', help = 'Input HDF5 file name(s).', is_list=False, values=['', None], type=str, optional=False, level = 0)
                   ]; #end of value InterNorm


#Variance stabilization transformation module settings
VST_options=[
                   Option('-m,--method', help = 'Variance stabilizing transformation.', values=[
                        Value('started-log', help = 'StartedLog', parameters=[
                            Option('--offset', help = 'Offset.', values=[50.0, None], type=float, targets=['/params'], level = 0),
                            ])
                        ], type=str, level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('h5dbname', help = 'Input HDF5 file name(s).', is_list=False, values=['', None], type=str, optional=False, level = 0)
                   ]; 
                   #end of value VST

# Options for peak filtering                   
PeakFilter_options=[
                   Option('-m,--method', help = 'Solvent/Matrix Peak Removal.', values=[
                        Value('kmeans', help = 'k-means cluster-driven solvent filter', parameters=[
                            Option('--nclusters', help = 'Number of clusters.', 
                                values=[2, None], type=int, targets=['/params'], level = 0),
                           # Option('--metric', help = 'Metric for clustering.', \
                           #     values=['correlation'], type=str, targets=['/params']),\
                            ])
                        ], type=str, level = 0),

                   ] + reference_set_options + [
                   
                   ] + logfile_options + [

                   Option('h5dbname', help = 'Input HDF5 file name(s).', is_list=False, values=['', None], type=str, optional=False, level = 0)
                   ]; 
                   #end of peak filtering options
                   
                   
Stat_analysis_options=[
                   Option('--method', help = 'Statistical analysis method to be used.', values = 

                           procconfig_options_for_methods, 
                   
                           type=str, targets=['/params'], level = 0), 
                   
                   Option('--model', help = 'Statistical analysis model to be used. Example: "C(group):C(dose)", where group and dose correspond to metadata column names "group" and "dose".', values=['auto', None], type=str, targets=['/params'], level = 0), 

                   Option('--samples', help = 'Coma separated selection of samples to be considered.', values=['*', None], is_list = True, type = str, targets=['/params'], level = 0),   
                   Option('--rts', help = 'Coma separated selection of retention time peaks or ranges to be considered.', values=['*', None], is_list = True, type = str, targets=['/params'], level = 0),   
                   Option('--rt_tolerance', help = 'Tolerance for RT peak matching, min.', values=[0.1, None], type = float, targets=['/params'], level = 0),   
                   Option('--output_prefix', help = 'Prefix to be added to output file names.', values=['%HDF5_file_name%_stat', 'export', 'output', 'results', '', None], type=str, targets=['/params'], level = 0),  
                   Option('--h5readpath', help = 'The path in HDF5 database for reading data.', values=['/spal2D_peakdetect', None], type=str, targets=['/params'], level = 1), 
                   Option('--h5writepath', help = 'The path in HDF5 database for writting results.', values=['/stat_analysis', None], type=str, targets=['/params'], level = 1), 

                   ] + logfile_options + [

                   Option('dbfilename', help =  'HDF5  database file with deposited multiple MS datasets.', values=['', None], type=str, optional=False, level = 0),
                   Option('exportpath', help =  'Output path for exporting results.', values=['', None], type=str, targets=['/params'], optional=True, level = 0),
                   ];
                   
                   
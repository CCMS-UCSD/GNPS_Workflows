# -*- coding: utf-8 -*-
"""
*********************************
Import Metadata into HDF5 
*********************************

Module for automated import of metadata into HDF5


run python.exe import_metadata.py --help to get info about parameters of the script

@author: Dr. Ivan Laponogov
"""

#===========================Import section=================================

#Importing standard and external modules
import h5py
import sys
import os
import time
import csv

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.procconfig import ImportMetaSet_options;

from proc.utils.cmdline import OptionsHolder
from proc.utils.timing import tic, toc;
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.printlog import printlog, start_log, stop_log, LoggingException;

#==========================================================================
#From here the main code starts


class HDF5FormatError(LoggingException):
    pass


def trydecode(value):
    """
    Check and convert value to number if possible.
    Return int if the fractional part is 0.
    Return float if the fractional part is not 0.
    Return boolean if True/False (not case sensitive)
    Return string in other cases
    
    Args:
        value: string value to be checked
        
    Returns:
        new value of the perceieved type
    """
    try:
        f = float(value);
        d = f - int(f);
        if d == 0.0:
            return int(f)
        else:
            return f;
    except:
        value = str(value)
        va = value.upper();
        if va == 'TRUE':
            return True
        elif va == 'FALSE':
            return False
        else:
            return value;


def write_meta_values(h5, h5writepath, sampleid, metids, metvals, overwrite = True):
    """
    Write meta values to the open h5 file according to the sample id.
    
    Args:
        h5: HDF5 File instance (opened and writeable).
        h5writepath: string containing path to the group of samples to add 
                     metadata to.
        sampleid: name of the sample, same as the name of the group containing 
                  sample data. Matching is case sensitive.
        metids:  list of metadata variable names
        metvals: list of metadata variable values
        overwrite: boolean, defines if already existing metadata values will be 
                   overwritten.
        
    Returns:
        None
    
    """
    group_name = h5writepath + sampleid;
    if group_name in h5:
        printlog('Adding metadata to %s...'%group_name);
        group = h5[group_name];
        
        if 'MetaData' in group:
            metagroup = group['MetaData'];
            if not isinstance(metagroup, h5py.Group):
                raise HDF5FormatError('Error! A dataset "MetaData" exists in %s of %s!'%(group_name, h5.filename));
        else:
            metagroup = group.create_group('MetaData');
        
        group.attrs['has_metadata'] = True;
        for i in range(len(metids)):
            metid = str(metids[i]);
            if metid != '':
                if not (metid in metagroup.attrs) or overwrite:
                    metagroup.attrs[metid] = trydecode(metvals[i]);
    else:
        printlog('%s not found in %s! Skipping...'%(group_name, h5.filename))
        
        
    
def import_metadata(parameters):
    """
    Import metadata from external file and write it to HDF5.
    
    """
    
    dbfilepath = parameters['dbfilename'];
    h5writepath = h5Base.correct_h5path(parameters['h5writepath'])
    
    infilename = os.path.abspath(parameters['metafilename']);
    
    with h5py.File(dbfilepath, 'a') as h5:
    
        if parameters['filetype'] == 'csv':
            with open(infilename, 'r') as infile:
                csv_reader = csv.reader(infile, delimiter = ',', quotechar = '"');
                index = -1;
                for row in csv_reader:
                    index += 1;
                    if index == 0:
                        metids = row[1:];
                    else:
                        sampleid = row[0];
                        metvals = row[1:];
                        minlen = min(len(metids), len(metvals));
                        write_meta_values(h5, h5writepath, str(sampleid), metids[0:minlen], metvals[0:minlen], parameters['overwrite'] == 'yes');


if __name__ == "__main__":
    tic();
    settings = OptionsHolder(__doc__, ImportMetaSet_options) 
    settings.description = 'Metadata import'   
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
   
    import_metadata(settings.parameters);
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();#
    printlog(settings.description_epilog);
    stop_log();

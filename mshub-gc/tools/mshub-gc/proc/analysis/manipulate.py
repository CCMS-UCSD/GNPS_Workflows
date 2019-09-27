# -*- coding: utf-8 -*-
"""
*********************************
HDF5 Manipulation Module
*********************************

Module for interactive and batched script-based manipulation of HDF5 datasets


run python.exe manipulate.py --help to get info about parameters of the script

@author: Dr. Ivan Laponogov
"""

#===========================Import section=================================

#Importing standard and external modules
import h5py
import sys
import os
import traceback
import time
import shlex

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.io.manageh5db import  split_hdf5_path, \
                                copy_attributes, \
                                abs_hdf5_path, \
                                rel_hdf5_path, \
                                get_items_list_from_hdf5, \
                                print_attributes,\
                                copy_hdf5_item,\
                                HDF5Error,\
                                LoggingIOError;
                                
from proc.procconfig import Manipulate_options;

from proc.utils.cmdline import OptionsHolder
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts


is_python_three = sys.version_info[0] > 2;



class HDF5Manipulator(object):
    def __init__(self, h5file, h5path, interactive, commandfilename = ''):
        self.h5file = h5file;
        self.h5path = h5path;
        self.interactive = interactive;
        self.commandfilename = commandfilename;
        

        
    def process_command_line(self, command_line):
        #shlex.whitespace_split = False;
        lex = shlex.shlex(command_line)
        lex.whitespace_split = False;
        lex.commenters = '';
        commands = list(lex);
        #command_lines = io.StringIO(command_line.decode('utf-8'));
        #commands = tokenize(command_lines.readline);
        print(commands)
        self.max_iter -= 1;
        return self.max_iter > 0;
        #command_line
    
    def process_commands(self, input_source):
        has_commands = True;
        self.max_iter = 5;
        while has_commands:
            continued_line = True;
            command_line = '';
            cont_prev_line = False;
            while continued_line:
                
                if input_source == sys.stdin:
                    if cont_prev_line:
                        prompt = '.' * len(self.h5path) + '>';
                    else:
                        prompt = self.h5path + '>';
                        
                    
                    sys.stdout.write(prompt);
                    sys.stdout.flush();
                
                line = input_source.readline();
                
                if line == '':
                    has_commands = False;   
                    break;
                line = line.rstrip('\n');
                if not line.endswith('\\'):
                    continued_line = False;
                    command_line = ' '.join([command_line, line]);
                    cont_prev_line = False;
                else:
                    command_line = ' '.join([command_line, line.rstrip('\\')]);
                    cont_prev_line = True;
                    
            has_commands = self.process_command_line(command_line) and has_commands;
            
        
    def run(self):
        self.cd(self.h5path);
        if interactive:
            self.process_commands(sys.stdin);
        else:
            with open(self.commandfilename, 'r') as finp:
                self.process_commands(finp);
                
    
    def cd(self, h5path):
        h5path = abs_hdf5_path(h5path, self.h5path);
        if h5path in h5file:
            item = h5file[h5path];
            if isinstance(item, h5py.Group):
                self.current_group = item;        
                self.h5path = h5path;
                printlog('Current path set to %s'%h5path);
            else:
                printlog('Error! Path %s does not point to a group!'%h5path);
        else:
            printlog('Error! Path %s does not exist!'%h5path);


    def ls(self, recursive = False, selection = '*', show_attributes = False, show_groups = True, show_datasets = True):

        source_path = abs_hdf5_path(selection, self.h5path);
        selected_items = get_items_list_from_hdf5(self.h5file, source_path, recursive);
        
        source_path = source_path.split('/')[:-1];
        source_path_len = len(source_path);

        for item_name in selected_items:
            item = self.h5file[item_name];
            item_relpath = '/'.join(item_name.split('/')[source_path_len:]);
            if isinstance(item, h5py.Group) and show_groups:
                printlog('[%s]'%item_relpath);
                if show_attributes:
                    print_attributes(item);
            elif isinstance(item, h5py.Dataset) and show_datasets:
                printlog(' %s '%item_relpath);
                if show_attributes:
                    print_attributes(item);
            else:
                printlog('?%s '%item_relpath);

        
        
        
    def cp(self, source, target):
        """
        Copy source to target path
        """
            
        target = abs_hdf5_path(target, self.h5path).rstrip('/');

        if not target in self.h5file:
            target_group = self.h5file.create_group(target);
        else:
            target_group = self.h5file[target];

        if not isinstance(target_group, h5py.Group):
            printlog('Error! Destination %s exists and it is not a group! Cannot copy %s!'%(target, source));
            return

        source_path = abs_hdf5_path(source, self.h5path);
        selected_items = get_items_list_from_hdf5(self.h5file, source_path, recursive = True);
        source_path = source_path.split('/')[:-1];
        source_path_len = len(source_path);
        for item in selected_items:
            printlog('Copying %s to %s...'%(item, target));
            rel_item = '/'.join(item.split('/')[source_path_len:]);
            copy_hdf5_item(self.h5file, item, target + '/' + rel_item);
        
    
    def rm(self, target):
        """
        Remove items defined by target
        """
        printlog('Removing %s...'%(target));
        targets = reversed(get_items_list_from_hdf5(self.h5file, abs_hdf5_path(target, self.h5path), recursive = True));
        for i in targets:
            del h5file[i];
    
    def mkdir(self, target):
        """
        Make group defined by target
        """
        target = abs_hdf5_path(target, self.h5path).rstrip('/');
        printlog('Creating group %s'%(target));
        if target in self.h5file:
            printlog('Error! %s already exists!'%target);
        else:
            self.h5file.create_group(target);
    
        
        

if __name__ == "__main__":
    settings = OptionsHolder(__doc__, Manipulate_options) 
    settings.description = 'Manipulation of HDF5 file'   
    settings.do = 'yes'   
    printlog(settings.program_description)   
    settings.parse_command_line_args()   
    
    
    parameters = settings.parameters;
    if parameters['logfile'] != '':
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'));
        printlog(settings.program_description, print_enabled = False);
    
    printlog('Started on %s '%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    printlog(settings.format_parameters())
    tic();    
    commandfilename = parameters['commandfilename'];
    if commandfilename == '':
        printlog('\nStarting interactive session...')
        interactive = True;
    else:
        printlog('\nStarting batched mode...')
        interactive = False;
        commandfilename = os.path.abspath(commandfilename)
        if not os.path.isfile(commandfilename):
            raise LoggingIOError('Command file %s not found!'%commandfilename);
    
    fname = os.path.abspath(parameters['dbfilename']);
    if not os.path.isfile(fname):
        printlog('File %s not found!'%fname);
    else:
        with h5py.File(fname, 'a') as h5file:
            h5path = parameters['h5path']; 
            printlog('Opened %s...'%fname);
            if not h5path in h5file:
                if interactive:
                    printlog('%s path in HDF5 not found! Going to root instead!'%h5path);
                    h5path = '/';
                else:
                    raise HDF5Error('%s path in HDF5 not found! Cannot continue in batch mode!'%h5path);
            
            manipulator_hdf5 = HDF5Manipulator(h5file, h5path, interactive, commandfilename);
            manipulator_hdf5.run();
   
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();

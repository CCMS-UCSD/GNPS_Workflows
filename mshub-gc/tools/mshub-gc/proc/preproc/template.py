# -*- coding: utf-8 -*-
"""
*******************************************************************
<Pipeline module template. Place Title here.>
*******************************************************************

<Place the module description here>

<The following line should be present for the script to work properly as the 
description is split into header and tail according to it. Header is displayed 
at the start of the program and tail - when it finishes:>

run python.exe <template>.py --help to get info about parameters of the script

<replace "<template>" in the line above with your module name! Do not change
the rest!>

<Place here what you want to display at the end of you module running time,
e.g. references to the methods used, author info, acknowledgements etc. Please,
also keep in mind this section is used for module documentation automatic
generation>

"""

#If you have questions regarding this template, please contact 
#Dr. Ivan Laponogov (i.laponogov@imperial.ac.uk)

#===========================Import section=================================

#Importing standard and external modules
#<these modules are the "must have" ones>
import os; 
import sys;
import traceback #This is for displaying traceback in try: except: constructs
import time;

#<these will likely be needed for hdf5 support and mathematical operations>
import h5py
import numpy as np

#<Add mode global/external modules here as needed>

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        #Use print here instead of printlog as printlog is not yet imported! 
        #The rest should have printlog in place of print.
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    #<Adjust relative path in the following line to point to the folder containing proc>
    #<Currently proc is located two folders above the one with the template.py>
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    #this should place the path for searching local modules at the front 
    #so that local path is found first and your script is not confused by possible
    #other versions in the search path
    sys.path.insert(0, module_path); 
    

#Import local/internal modules

#Import command line options set for <your> module from procconfig.
#<replace "Template_option" with the option set name you created for your module.>
#<See procconfig for template option set.>
from proc.procconfig import Template_options as cmdline_options;

#Manager for command line options
from proc.utils.cmdline import OptionsHolder

#Timing functions for standard stats output
from proc.utils.timing import tic, toc;

#Printing with logging module for dual-channel output (see module for details)
#<please use printlog instead of print in your code starting
#form here for any user print output to be potentially also logged.
#You are welcome to use temporary print functions for development,
#but using printlog is strongly recommended for user targeted output.>
#<Please also note that printlog takes one string for printing,
#so format printing statements accordingly. printlog(a,b,c,d...) will
#not work in the current version. Use printlog("(%s,%s,%s,%s,...)"%(a,b,c,d,...))
#for equivalent output.>
from proc.utils.printlog import printlog, start_log, stop_log, LoggingException;
#Please inherit your custom Exceptions from LoggingException and use them
#to both display and log the error message!

#<Import further local/internal modules here and, please, keep them grouped/sorted
#according to their full paths. E.g. from proc.utils..... should go as one bunch.
#See other modules for examples.>
#==========================================================================
#Custom Exception definitions - replace with your own
class CustomException(LoggingException):
    pass

#==========================================================================
#From here the main code starts



#----------------------!!!!!!!!!!!!!!!!!!!!!!!!---------------------------
#In your code if you use try: except: construct and possibly could encounter
#an error, but intend to continue executing code afterwards, then please make
#sure not to mask the exception with simple "pass" or print('Error!');
#Report full exception details and its trace to the log/screen in order to make
#it possible to track the exceptions and make sure that no hidden errors are
#lurking around making unexpectable mess in your results. Be transparent!
#Debugging hidden errors is tough, finding out your published results are rubbish
#because you did not even know there were errors is even worse. ;-)
#
#Please use the construct of the sort or better:
#
#try:
#    <your code which may fail, but should not stop the whole program>
#except Exception as inst:
#    #your message here    
#    printlog('%s. %s: Failed to be corrected' %(dataindex, datasetid))
#    #actuall error message
#    printlog(inst)
#    #traceback of where the error occured
#    traceback.print_exc():
#
#---------------------------------------------------------------------------

#Please also inherit your classes from object or its descendants to make the
#following call to the parent class init work:
#def __init__(self):
#    super(type(self), self).__init__()




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

    settings.parse_command_line_args()   

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
    
    
    
    
    #<Run your own processing functions here providing them with parameters 
    #from settings/command line parser. >
   
    #Finalization stats and timing
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    
    #Print description ending here
    printlog(settings.description_epilog);
    
    #stop logging
    stop_log();



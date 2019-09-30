# -*- coding: utf-8 -*-
"""
*******************************************************************
Per-sample Continuous Data Plotting routine
*******************************************************************

This module allows to generate plots individually for samples
displaying distribution of the signal in mz and rt plane.



run python.exe plot_samples.py --help to get info about parameters of the script

"""

#===========================Import section=================================

#Importing standard and external modules
import os; 
import sys;
import traceback #This is for displaying traceback in try: except: constructs
import time;

import h5py
import numpy as np

from bokeh.plotting import figure, ColumnDataSource;
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import gridplot #, column
from bokeh.palettes import Inferno256;
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker, HoverTool;


#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        #Use print here instead of printlog as printlog is not yet imported! 
        #The rest should have printlog in place of print.
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    #this should place the path for searching local modules at the front 
    #so that local path is found first and your script is not confused by possible
    #other versions in the search path
    sys.path.insert(0, module_path); 
    

#Import local/internal modules

from proc.procconfig import Plot_samples_options as cmdline_options;


import proc.io.manageh5db as mh5

from proc.utils.cmdline import OptionsHolder
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base



#==========================================================================

def _make_top_rt_plot(crt, sp, title, plot_width, plot_height, use_global_max = False, global_max = 0.0):
    mincrt = crt[0]
    maxcrt = crt[-1]

    if use_global_max:
        maxv = global_max;
    else:
        maxv = np.max(sp);
    
    lcrt = [];
    lsp = [];
    
    crt = np.array(crt);
    
    crt = crt[0:crt.shape[0]:5];
    sp = sp[0:sp.shape[0]:5, :];
    
    crt = crt.tolist()
    
    for i in range(sp.shape[1]):
        lcrt.append(crt);
        lsp.append(sp[:, i].tolist());
    
    
    source = ColumnDataSource(data=dict(
       fx =  lcrt,
       fy =  lsp,
    ))     
    
    #hover = HoverTool(tooltips=[
    #    ("rt (min)", "@fx"),
    #    ("Intensity", "@fy"),
    #   ])
    
    s = figure(plot_width = plot_width, 
                   plot_height = plot_height, 
                   title = title, 
                   tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
                   toolbar_location = "above",
                   toolbar_sticky = False,
                   x_range = (mincrt, maxcrt),
                   y_range = (0, maxv), 
                   y_axis_location = "right"
                   );

    #s.add_tools(hover);
      
    s.multi_line(xs = 'fx', ys = 'fy', line_width = 1, color = "firebrick", source = source);

    return s

    

def _make_bottom_rt_plot(crt, cmz, sp, title, plot_width, plot_height, is_log = True, use_global_max = False, global_max = 0.0):
    
    #crt = np.array(crt) / 60.0;
    sx = sp.shape[0];
    sy = sp.shape[1];
    
    #dx = crt[1] - crt[0];
    #dy = cmz[1] - cmz[0];
    
    cx = np.zeros(sp.shape, dtype = np.float64);
    cy = np.zeros(sp.shape, dtype = np.float64);
    
    cx[:, :] = crt[:].reshape((sx, 1));
    
    cy[:, :] = cmz[:].reshape((1, sy));
    
    if use_global_max:
        max_sp = global_max;
    else:
        max_sp = np.max(sp);
    
    if is_log:
        sp = np.log(sp + 1.0);
        max_sp = np.log(max_sp + 1.0);
    
    min_sp = np.min(sp[sp>0.0]);
    
    #if max_sp - min_sp > 0.0:
    #    log_sp = (log_sp - min_sp)/(max_sp - min_sp) * 255;
        
    
    #for j in range(log_sp.shape[0]):
    #    color.append(Inferno256[log_sp[j]]);
        
    #sp[0:2, :] = 12;
    
    color_mapper = LinearColorMapper(palette = Inferno256, low = min_sp, high = max_sp);
        
    ticker = BasicTicker();
    
    s = figure(plot_width = plot_width, 
               plot_height = plot_height, 
               title = title, 
               x_range = (crt[0], crt[-1]),
               y_range = (cmz[0], cmz[-1]),
               tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
               toolbar_location = "above",
               toolbar_sticky = False,
               y_axis_location = "right",
               background_fill_color = '#000000');
    
    s.image(image = [sp.transpose()], x = crt[0], y = cmz[0], dw = crt[-1] - crt[0], dh = cmz[-1] - cmz[0], color_mapper = color_mapper)    
    
    s.xgrid.grid_line_color = None;
    s.ygrid.grid_line_color = None;
    
    
    color_bar = ColorBar(color_mapper = color_mapper, 
                         ticker = ticker, 
                         label_standoff = 12, 
                         border_line_color = None, 
                         location = (0, 0),
                         orientation = "horizontal")        

    s.add_layout(color_bar, 'below');
   
    return s




def generate_sample_plot(h5file, dataset_path, dataset_index, dataset_name, output_file, crt, cmz, plot_width, top_plot_height, bottom_plot_height, use_global_max, global_max):
    sp_set = dataset_path + '/sp';
    if not (sp_set in h5file):
        printlog('Error! sp not found in %s ! Skipping...'%(dataset_path))
        return
        
    sp = np.array(h5file[sp_set]); 
    
    #sp_int = np.sum(sp, axis = 1);
    
    crt = np.array(crt);
    crt = crt / 60.0;
    
    top_plot = _make_top_rt_plot(crt, sp, '%s. RT Integral profile, linear scale'%dataset_name, plot_width, top_plot_height, use_global_max, global_max);
        
    bottom_plot = _make_bottom_rt_plot(crt, cmz, sp, '%s. Full profile, log scale'%dataset_name, plot_width, bottom_plot_height, True, use_global_max, global_max);
    #bottom_plot2 = _make_bottom_rt_plot(crt, cmz, sp, '%s. Full profile, linear scale'%dataset_name, plot_width, bottom_plot_height, False, use_global_max, global_max);

    bottom_plot.x_range = top_plot.x_range;
    #bottom_plot2.x_range = top_plot.x_range;
    #bottom_plot2.y_range = bottom_plot.y_range;
    
        
    script, div = components(gridplot([[top_plot], 
                                       [bottom_plot], 
                                       #[bottom_plot2]
                                       ]));
    
    with open(output_file, 'w') as fspec:
        
        fspec.write(    '\n'.join([
                        '<!DOCTYPE html>',
                        '<html lang="en">',
                        '    <head>',
                        '        <meta charset="utf-8">',
                        '        <title>RT Spectrum for all peaks</title>',
                                 CDN.render(),                        
                        '        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">',
                        '    </head>',
                        '    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>',
                        '    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>',
                        '    <body>',
                                div,
                        '    </body>',
                            script, 
                        '<style>',
                        '</style>',
                        '    </html>',
                        ]));
        
    


def export_HTML_list_of_samples_to_file(dbfilepath, h5readpath, output_prefix, plot_width = 900, top_plot_height = 300, bottom_plot_height = 400, use_global_maximum = True):            
    printlog('Exporting HTML view from [%s]%s to %s...'%(dbfilepath, h5readpath, output_prefix));
    
    with h5py.File(dbfilepath, 'r') as h5file:
        
        if not os.path.exists(output_prefix):
            os.makedirs(output_prefix);
        
        h5readpath  = h5Base.correct_h5path(h5readpath)    
        
        dataset_names = mh5.get_dataset_names(h5file, dataset_names = [], pathinh5 = h5readpath[:-1])
        
        if not dataset_names:
            printlog('No datasets found! Nothing to do!')
            return

        dataset_count = len(dataset_names);
        
        
        all_rts_set = h5readpath + 'crt';
        if not (all_rts_set in h5file):
            printlog('Error! crt not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return
        
        crt = h5file[all_rts_set]; 
        
        
        all_mzs_set = h5readpath + 'cmz';
        if not (all_mzs_set in h5file):
            printlog('Error! cmz not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return
        
        cmz = h5file[all_mzs_set]; 
        
        
        
        if not os.path.exists('%s/samples'%output_prefix):
            os.makedirs('%s/samples'%output_prefix);
        
        with open('%s/index.html'%output_prefix, 'w') as fout:
            fout.write('\n'.join([
            '<!DOCTYPE html>',
            '<html>',
            '<frameset cols="15%,85%">',
            '<frame src="sample_list.html">',
            '<frame src="samples/sample_0.html" name="MSSpectrum">',
            '</frameset>',
            '</html>',
            ]));
            
            
        with open('%s/sample_list.html'%output_prefix, 'w') as fout:

            fout.write('\n'.join([
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Samples</title>',
            '</head>',
            '<body>',
            '    <table border=1>',
            '    <tr><th>Samples</th></tr>']));

            global_max = 0.0;
            #global_max_sum = 0.0;
            
            if use_global_maximum:
                printlog('Evaluating global maximum...')
                for i in range(dataset_count):
                    printlog('Sample: %s of %s'%(i+1, dataset_count));
                    sp_set = h5readpath + dataset_names[i].lstrip('/') + '/sp';
                    if not (sp_set in h5file):
                        printlog('Error! sp not found in %s ! Skipping...'%(h5readpath + dataset_names[i].lstrip('/')))
                    else:
                        sp = h5file[sp_set]
                        m = np.max(sp); 
                        #mm = np.max(np.sum(sp, axis = 1));
                        global_max = max(m, global_max);
                        #global_max_sum = max(mm, global_max_sum)
                

            for i in range(dataset_count):
                printlog('Sample: %s of %s'%(i+1, dataset_count));
                
                generate_sample_plot(h5file, 
                                     h5readpath + dataset_names[i].lstrip('/'), 
                                     i, 
                                     dataset_names[i].lstrip('/'), 
                                     output_prefix + '/samples/sample_%s.html'%i, 
                                     crt, 
                                     cmz, 
                                     plot_width, 
                                     top_plot_height, 
                                     bottom_plot_height, use_global_maximum, global_max);
                
                fout.write('\n'.join([
                        '<tr><td>%s. '%(i+1),
                        '<a href="samples/sample_%s.html" target="MSSpectrum">%s</a>'%(i, dataset_names[i].lstrip('/')),
                        '</td></tr>',
                        ]))

            fout.write('\n'.join([
                '    </table>',
                '</body>',
                '</html>',
                ]));


        printlog('Done')        




def do_sample_plots(dbfilepath, params = {'h5readpath':'/spproc2D_peakdetect', 
                                    'h5fullprofile':'/spproc2D',
                                    'output_prefix':'%HDF5_file_name%', 
                                    } ):
    
    """
    Generates HTML report for analysis.
    
    Args:
    
        dbfilepath: a user-specified path to the h5 database file
                    
        params: parameters to be used for export:
            h5readpath - path inside HDF5 to the processed dataset
            output_prefix - prefix to be used for the output files
            
    """     
    
    params['h5readpath'] = h5Base.correct_h5path(params['h5readpath'])

    dbfilepath = os.path.abspath(dbfilepath);
    
    output_prefix = params['output_prefix'];
    if '%HDF5_file_name%' in output_prefix:
        fname = os.path.splitext(os.path.basename(dbfilepath))[0];
        output_prefix = output_prefix.replace('%HDF5_file_name%', fname + '.samples');
        
    export_path = params['exportpath'];
    if export_path != '':
        export_path = os.path.abspath(export_path);
    else:
        export_path = os.path.split(dbfilepath)[0];
    
    output_prefix = os.path.join(export_path, output_prefix);
    
    fpath = os.path.split(output_prefix)[0];
    
    if not os.path.exists(fpath):
        os.makedirs(fpath);
        
    export_HTML_list_of_samples_to_file(dbfilepath, params['h5readpath'], output_prefix, 
                             params['plot_width'], params['top_plot_height'], params['bottom_plot_height'], str(params['global_maximum']).lower() == 'yes');

                    
    return


#===========================================================================

#Here the main part of the code which is executed when the module is run starts
if __name__ == "__main__": 
    tic(); #Start default timer
    
    #Create command line options handler
    settings = OptionsHolder(__doc__, cmdline_options); 
    
    #Set module short description. <Replace 'Template module' with your description>
    settings.description = 'Individual sample plotting';
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
    

    do_sample_plots(settings.parameters['dbfilename'],
                     params = settings.parameters['params'])
   
    #Finalization stats and timing
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    
    #Print description ending here
    printlog(settings.description_epilog);
    
    #stop logging
    stop_log();



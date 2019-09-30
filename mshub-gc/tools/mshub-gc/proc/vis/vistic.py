#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
*********************************************
Total Ion Chromatogram Visualization module
*********************************************

The module is designed to visualize raw or processed total ion chromatograms 
(tics) across multiple samples

run python.exe vistic.py --help to get info about parameters of the script

"""

#===========================Import section=================================

#Importing standard and external modules
import os
import numpy as np
import traceback
import sys
import time

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__":
    if sys.byteorder != 'little':
        print('Only little endian machines currently supported! bye bye ....')
        quit()
    module_path = os.path.abspath('%s/../..' % os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, module_path)

#Import local/internal modules
from proc.procconfig import TICvis_options

import proc.io.manageh5db as mh5

from proc.utils.cmdline import OptionsHolder
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts


def view_tics(dbfilepath, method='', params=''):
    printlog('\nExtracting TICs.....')

    h5readpath = params['h5readpath']
    sp = get_data(dbfilepath, h5readpath)
    figtitle = 'Total Ion Chromatograms'
    dirname = os.path.dirname(dbfilepath)

    #screenwidth = 800
    #screenheight = 600

    # if method == 'pyplot':
    #
    #     mydpi = 96
    #     plt.figure(figsize=(screenwidth / mydpi, screenheight / mydpi), dpi=mydpi)
    #     plt.plot(crt, tics)
    #     plt.xlabel('Time(s)')
    #     plt.ylabel('Intensity')
    #     plt.title(figtitle)
    #     plt.show()

    if method == 'bokeh':

        from bokeh.plotting import figure, show, save, output_notebook, output_file, ColumnDataSource
        from bokeh.io import push_notebook
        from bokeh.models import HoverTool

        #if params['inline'] == 'yes':
        #    params['inline'] = 'yes'
            # output_notebook()

        #else:
        if params['outputfile'] == '':
            filename = 'bp' + time.strftime("%H%M_%d_%m_%Y") + '.html'
        else:
            filename = params['outputfile']
        
        output_file(os.path.join(dirname, filename))

        source = ColumnDataSource(sp)

        p = figure(width=params['plot_width'], height=params['plot_height'],
                   title=figtitle, x_axis_label='Time(mins)', y_axis_label='Intensity')

        p.multi_line(xs='x', ys='y',
                     line_width=1, line_color='color', line_alpha=0.6,
                     hover_line_color='color', hover_line_alpha=1.0,
                     source=source)

        p.add_tools(HoverTool(show_arrow=False, line_policy='next', tooltips=[
            ('id', '@id')]))
        
        try:    
            p.toolbar.active_inspect = [None]
        except:
            pass
        #if params['inline'] == 'yes':
        #    show(p)
            # push_notebook(handle=hnotebook)
            # push_notebook(handle=handle)
        #else:
        if params['display'] == 'yes':
            show(p)
        else:
            save(p)


def colorgenerator(N):
    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100
    colors = ["#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(np.floor(50 + 2 * x), np.floor(30 + 2 * y))]
    return colors


def get_data(dbfilepath, h5readpath):
    """ Extract data from the h5file and output as a dictionary of 'x', 'y', 'ids', and 'colors' for each sample """
    if h5readpath[0] != '/':
        h5readpath = '/'.join(['', h5readpath])

    if os.path.isfile(dbfilepath):
        datasets = mh5.get_dataset_names(dbfilepath, dataset_names=[], pathinh5=h5readpath)
        if not datasets:
            printlog(dbfilepath + ' database file doesn''t contain any MSI datasets')
            return
    else:
        printlog(str(dbfilepath) + ' database file is not found')
        return

    sizesp = mh5.load_dataset(dbfilepath, '/'.join([h5readpath, 'sizesp']))
    tics = np.zeros((sizesp[0], sizesp[2]))
    crt = mh5.load_dataset(dbfilepath, '/'.join([h5readpath, 'crt']))
    j = -1
    dataidx = np.array([])
    for datasetid in datasets:
        j = j + 1
        try:
            sp = mh5.load_dataset(dbfilepath, ''.join([h5readpath, datasetid, '/sp']))
            tics[:, j] = np.sum(sp, axis=1)
            dataidx = np.append(dataidx, j)
        except Exception as inst:
            printlog(os.path.basename(datasetid) + ": Failed to readin")
            printlog(inst)
            traceback.print_exc()
            
            
    dataidx = dataidx.astype(int)
    datasets = list(map(datasets.__getitem__, (dataidx)))
    tics = tics[:, dataidx]
    nrows, ncols = tics.shape
    sp = {'x': [], 'y': [], 'id': [], 'color': []}
    for i in range(ncols):
        sp['x'].append(crt/60)
        sp['y'].append(tics[:, i])
        sp['id'].append(datasets[i])
    sp['color'] = colorgenerator(ncols)
    return sp

def get_average_profile(dbfilepath, dataid=''):
    if os.path.isfile(dbfilepath):
        datasets = mh5.get_dataset_names(dbfilepath, dataset_names=[])
        if not datasets:
            printlog(dbfilepath + ' database file doesn''t contain any MSI datasets')
            return
    else:
        printlog(str(dbfilepath) + ' database file is not found')
        return

    sizesp = mh5.load_dataset(dbfilepath, 'sizesp')
    sp_mean = np.zeros((sizesp[0], sizesp[1]))
    crt = mh5.load_dataset(dbfilepath, 'crt')
    
    #crt = crt / 60;

    j = -1

    dataidx = np.array([])
    for datasetid in datasets:
        j = j + 1
        try:
            sp = mh5.load_dataset(dbfilepath, datasetid + dataid)
            sp_mean = sp_mean + sp
            dataidx = np.append(dataidx, j)
        except Exception as inst:
            printlog(os.path.basename(datasetid) + ": Failed to readin")
            printlog(inst)
            
            
    dataidx = dataidx.astype(int)
    datasets = list(map(datasets.__getitem__, (dataidx)))
    sp_mean = sp_mean / len(dataidx)

    return sp_mean, crt, datasets


if __name__ == "__main__":
    tic();
    settings = OptionsHolder(__doc__, TICvis_options)
    settings.description = 'Intra-Sample Peak Alignment'
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
        start_log(parameters['logfile'], overwrite_existing = (parameters['overwrite_logfile'] == 'yes'));
        printlog(settings.program_description, print_enabled = False);
    
    
    printlog('Started on %s ...'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    
    printlog(settings.format_parameters())
    
    view_tics(settings.parameters['dbfilename'],
              method=settings.parameters['method'],
              params=settings.parameters['params'])

    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog)
    stop_log();
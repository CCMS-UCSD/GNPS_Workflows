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
from proc.preproc.peakdetect import median_threshold
from proc.utils.signalproc import smooth1D
from scipy.interpolate import interp1d

from bokeh.plotting import figure, show, save, output_notebook, output_file, ColumnDataSource
from bokeh.io import push_notebook
from bokeh.models import HoverTool


#==========================================================================
#From here the main code starts


def view_tics(dbfilepath, method='', params=''):
    
    printlog('\nExtracting TICs.....')

    h5readpath = params['h5readpath']
    data = get_data(dbfilepath, h5readpath)
    figtitle = 'Total Ion Chromatograms'
    dirname = os.path.dirname(dbfilepath)


    if params['outputfile'] == '':
        filename = 'bp' + time.strftime("%H%M_%d_%m_%Y") + '.html'
    else:
        filename = params['outputfile']
        
    output_file(os.path.join(dirname, filename))

    source = ColumnDataSource(data)

    p = figure(width=params['plot_width'], height=params['plot_height'],
                   title=figtitle, x_axis_label='Time(mins)', y_axis_label='Intensity')

        
    p.multi_line(xs = 'x', ys = 'y',
                 line_width = 1, line_color = 'color', line_alpha = 0.6,
                 hover_line_color = 'color', 
                 hover_line_alpha = 1.0,
                 source = source)
                 
    print(data.keys())             
                     
    if 'histc' in data:
        p.line(x = 'hx', y = 'histc', line_width=1, line_color = 'firebrick', source = source);
    
    if 'histc_threshold' in data:
        p.line(x = 'hx', y = 'histc_threshold', line_width = 2, line_color = 'navy', source = source);
            
    if 'ref2D' in data:
        p.line(x = 'refx', y = 'ref2D', line_width = 1, line_color = 'red', source = source)
            
    if 'picked_peaks' in data:
        p.circle(x = 'peak_x', y = 'picked_peaks', color = 'peak_color', size = 3, source = source)
            

    p.add_tools(HoverTool(show_arrow=False, line_policy='next', tooltips=[
            ('id', '@id')]))
        
    try:    
        p.toolbar.active_inspect = [None]
    except:
        pass
        
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
    
    data = {'x': [], 'y': [], 'id': [], 'color': []}
    
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
    crt = mh5.load_dataset(dbfilepath, '/'.join([h5readpath, 'crt']))
    
    try:
        ref2D = mh5.load_dataset(dbfilepath, '/'.join([h5readpath, 'ref2D']))
        print(ref2D.shape)
    except:
        ref2D = None;
    
    
    try:
        histc = mh5.load_dataset(dbfilepath, '/'.join([h5readpath+'_peakdetect', 'clustering_histogram']))
        print(np.min(histc))        
        print(np.max(histc))
    except:
        histc = None


    try:
        histc_threshold = mh5.load_dataset(dbfilepath, '/'.join([h5readpath+'_peakdetect', 'clustering_histogram_threshold']))
        print(np.min(histc_threshold))        
        print(np.max(histc_threshold))
    except:
        histc_threshold = None

    
    tics = np.zeros((sizesp[0], sizesp[2]))
    
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
    
    if not (histc is None):
        #histc[histc<=threshold] = 0
        '''
        if 'histc' in data:
            p.line(x = 'hx', y = 'histc', line_width=1, line_color = 'firebrick', source = source);
    
        if 'histc_threshold' in data:
            p.line(x = 'hx', y = 'histc_threshold', line_width = 2, line_color = 'navy', source = source);
            
        if 'ref2D' in data:
            p.line(x = 'refx', y = 'ref2D', line_width = 1, line_color = 'red', source = source)
            
        if 'picked_peaks' in data:
            p.circle(x = 'peak_x', y = 'picked_peaks', color = 'peak_color', size = 3, source = source)
    
        '''
        med_int = np.median(tics,axis=1).flatten()[0:-1]  + 1
        med_int = np.sqrt(med_int)
        histc =  med_int * histc       
        mv = np.max(tics.flatten())
        mv = mv/np.max(histc)
        threshold = median_threshold(histc);
        threshold *= mv
        histc *= mv;
        
        dd = int(len(histc)/100) - 1;
        
        dx = np.zeros((dd,), dtype = np.float64);
        dy = np.zeros((dd,), dtype = np.float64);
        
        for i in range(dd):
            dx[i] = np.mean(crt[i*100:i*100+100])
            dy[i] = median_threshold(histc[i*100:i*100+100])
       
        dy  = smooth1D(dx,dy,10) 
        dx[0]  = np.min(crt)
        dx[-1] = np.max(crt)
        fit = interp1d(dx,dy,kind='cubic')       
        fitted_threshold = fit(crt)
        

    nrows, ncols = tics.shape
    
    
    for i in range(ncols):
        data['x'].append(crt/60)
        data['y'].append(tics[:, i])
        data['id'].append(datasets[i])

    data['color'] = colorgenerator(ncols)
    
    
    return data

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
    settings.parse_command_line_args()
    
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
# -*- coding: utf-8 -*-
"""

*******************************************************************
Exporting output data module 
*******************************************************************

The module is designed to generate HTML report covering results of 
pre-processing.

run python.exe report.py --help to get info about parameters of the script

"""

#===========================Import section=================================

#Importing standard and external modules
import os
import sys;
import h5py
import numpy as np
import time

from bokeh.plotting import figure, ColumnDataSource;
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import gridplot #, column
from bokeh.palettes import Inferno256;
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker, HoverTool;

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
from proc.procconfig import Reporting_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.h5utils import h5read_strings;
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, start_log, stop_log;

#==========================================================================
#From here the main code starts



median_palette_positive = [];
median_palette_negative = [];
median_palette = [];

for i in range(256):
    median_palette_negative.append(('#%02x%02x%02x'%(0, 255 - i, 255 - i)).upper());
    median_palette_positive.append(('#%02x%02x%02x'%(i, 0, 0)).upper());
    vv = (float(i) - 255/2.0)*2.0;
    v = int(abs(vv));
    if vv >= 0:
        median_palette.append(('#%02x%02x%02x'%(v, 0, 0)).upper());
    else:
        median_palette.append(('#%02x%02x%02x'%(0, v, v)).upper());



def _make_top_rt_plot(x, dx, y, y0, minx, maxx, fx, fy, fminx, fmaxx, title, is_log = False, plot_width = 900, plot_height = 300):
    
    dx = dx / 2.0;
    
    source = ColumnDataSource(data=dict(
       top =  list(y),
       bottom =  list(y0),
       left =  list(x - dx),
       right = list(x + dx),
       desc = list(x),
       intens = list(y),
       peakno = range(1, len(x)+1)
    ))
    
    source2 = ColumnDataSource(data=dict(
       fx =  list(fx),
       fy =  list(fy),
       intens = list(fy),
       desc = list(fx),
       peakno = ['N/A']*len(fx)
    ))     
    
    i = 0;
    px = x[i];
    count_x = len(x);
    pp = source2.data['peakno'];
    
    for j in range(len(fx)):
        tx = fx[j];
        if tx > px + dx:
            i += 1;
            if i >= count_x:
                break;
            else:
                px = x[i];
        if (tx <= px + dx) and (tx >= px-dx):
            pp[j] = i+1;
    
    
    hover = HoverTool(tooltips=[
        ("Peak No", "@peakno"),
        ("rt (min)", "@desc"),
        ("Integral/Intensity", "@intens"),
       ])
    
    if is_log:
        s = figure(plot_width = plot_width, 
                   plot_height = plot_height, 
                   title = title, 
                   tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
                   toolbar_location = "above",
                   toolbar_sticky = False,
                   x_range = (min(minx, fminx), max(maxx, fmaxx)),
                   y_axis_location = "right",
                   y_axis_type = "log"
                   );
    else:
        s = figure(plot_width = plot_width, 
                   plot_height = plot_height, 
                   title = title, 
                   tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
                   toolbar_location = "above",
                   toolbar_sticky = False,
                   x_range = (min(minx, fminx), max(maxx, fmaxx)),
                   y_axis_location = "right"
                   );

    s.add_tools(hover);
    

    s.quad(top = 'top', bottom = 'bottom', left = 'left',
       right = 'right', color = "navy", source = source)
      
    s.line('fx', 'fy', line_width=2, color = "firebrick", source = source2);

    return s




def _make_bottom_rt_plot(x, dx, y, minx, maxx, dataset_count, dataset_names, title, plot_width = 900, plot_height = 400):
    
    sx = y.shape[1];
    sd = y.shape[0];

    cx = np.zeros(y.shape, dtype = np.float64);
    cy = np.zeros(y.shape, dtype = np.float64);
    dcx = np.zeros(y.shape, dtype = np.float64);
    crt = np.zeros(y.shape, dtype = np.float64);
    
    dx = np.full(x.shape, fill_value = dx, dtype = np.float64);

    ddx = np.diff(x);
    
    ddx_count = len(ddx);
    
    rt = np.array(x);
    
    start_i = -1;    
    while start_i < ddx_count - 1:
        start_i += 1;
        if ddx[start_i] == 0.0:
            end_i = start_i;
            for j in range(start_i + 1, ddx_count):
                if ddx[j] == 0.0:
                    end_i = j;
                else:
                    break;
            ncount = end_i - start_i + 2;
            
            for j in range(start_i, start_i + ncount):
                x[j] = x[j] - 0.5 * dx[j];
                dx[j] = dx[j] / ncount;
                x[j] = x[j] + (j - start_i) * dx[j] + 0.5 * dx[j];
            
            start_i = end_i;
            
    
    for j in range(sd):
        cx[j, :] = x[:];
        dcx[j, :] = dx[:];
        crt[j, :] = rt[:];
    
    d = np.array(range(sd), dtype = np.float64);
    
    for j in range(sx):
        cy[:, j] = d[:];


    #n_samples, n_crt
    mask = y > 0.0;
    
    offset = np.median(y[mask]);        
    cvl = np.zeros(y.shape, dtype = np.float64);
        
    y[mask] = y[mask] + offset;
    
    cvl[mask] = np.log(y[mask]);
    
    med = np.zeros(cvl.shape, dtype = np.float64);
    
    for i in range(cvl.shape[1]):
        mm = cvl[mask[:, i], i];
        if len(mm) > 0:
            med[:, i] = np.median(mm);

    cvl[mask] = cvl[mask] - med[mask];

    lmin_y = np.min(cvl[mask]);
    lmax_y = np.max(cvl[mask]);
    
    span = max(abs(lmin_y), abs(lmax_y))
    
    mask = mask.reshape((sx*sd,));
    cvl = cvl.reshape((sx*sd,));
    cx = cx.reshape((sx*sd,));
    cy = cy.reshape((sx*sd,));
    dcx = dcx.reshape((sx*sd,));
    crt = crt.reshape((sx*sd,));
    
    cvl = cvl[mask];
    cx = cx[mask];
    cy = cy[mask];
    dcx = dcx[mask];
    crt = crt[mask];
    
    sample = [];
    color = [];
    
    #cvl = (cvl / span) * 127 + 127;
    
    sample_no = np.add(cy, 1).astype(dtype = np.int32).tolist();
    left = np.subtract(cx, dcx * 0.5).tolist();
    right = np.add(cx, dcx * 0.5).tolist();
    top = np.add(cy, 1).tolist();
    bottom = cy.tolist();
    rt = crt.tolist();
    
    for j in range(len(cy)):
        sample.append(dataset_names[int(cy[j])].lstrip('/'));
            
    for j in range(len(cy)):
        color.append(median_palette[int((1 + cvl[j]/span) * 127.5)]);
        
    intens = cvl.tolist();
        
    source = ColumnDataSource(data=dict(
       top = top,
       bottom = bottom,
       left = left,
       right = right,
       sample = sample,
       sample_no = sample_no,
       rt = rt,
       intens = intens,
       color = color,
    ))
    
       
    hover = HoverTool(tooltips=[
        ("Sample No", "@sample_no"),
        ("Sample", "@sample"),
        ("rt (min)", "@rt"),
        ("LogInt-median(LogInt)", "@intens"),
    ])
    
    color_mapper = LinearColorMapper(palette = median_palette, low = -span, high = span);
        
    ticker = BasicTicker();
    
    s = figure(plot_width = plot_width, 
               plot_height = plot_height, 
               title = title, 
               x_range = (minx, maxx),
               y_range = (0, dataset_count),
               tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
               toolbar_location = "above",
               toolbar_sticky = False,
               y_axis_location = "right",
               background_fill_color = '#ffffff');
    
    s.xgrid.grid_line_color = None;
    s.ygrid.grid_line_color = None;
    s.add_tools(hover);
    
    s.quad(top = 'top', bottom = 'bottom', left = 'left',
       right = 'right', color = 'color', source = source);        
    
    color_bar = ColorBar(color_mapper = color_mapper, 
                         ticker = ticker, 
                         label_standoff = 12, 
                         border_line_color = None, 
                         location = (0, 0),
                         orientation = "horizontal")        

    s.add_layout(color_bar, 'below');
    
   
    return s


def _generate_metatable(h5file, dbfilepath, h5readpath, output_prefix, dataset_names):
    printlog('Generating MetaData table...');
    dataset_count = len(dataset_names);

    metacolumns = set();
    for dataset_name in dataset_names:
        group_name = h5readpath + dataset_name;
        group = h5file[group_name];
        if 'MetaData' in group:
            metagroup = group['MetaData'];
            for attribute in metagroup.attrs.keys():
                metacolumns.add(attribute);
    metacolumns = sorted(list(metacolumns));
        
    if not metacolumns:
        return False;
    
    with open('%s/metadata.html'%(output_prefix), 'w') as fspec:
        fspec.write(    '\n'.join([
        '<!DOCTYPE html>',
        '<html lang="en">',
        '    <head>',
        '        <meta charset="utf-8">',
        '        <title>MetaData</title>',
        '    </head>',
        '    <body>',
        '       <table border=1>',
        ]));
        
        fspec.write('           <tr><th>N</th><th>Sample</th>\n');
        for s in metacolumns:
            fspec.write('            <th>%s</th>\n'%s);
        fspec.write('           </tr>\n');


        for index in range(len(dataset_names)):
            dataset_name = dataset_names[index];
            group_name = h5readpath + dataset_name;
            group = h5file[group_name];
            fspec.write('<tr><td>%s</td><td>%s</td>\n'%(index, dataset_name.lstrip('/')));
            if 'MetaData' in group:
                metagroup = group['MetaData'];
                for attribute in metacolumns:
                    if attribute in metagroup.attrs:
                        value = metagroup.attrs[attribute];
                    else:
                        value = '';
                    fspec.write('<td>%s</td>'%value);
            fspec.write('</tr>\n');
            
    
        fspec.write(    '\n'.join([
        '       </table>',
        '    </body>',
        '    </html>',
        ]));

    
                
    
    return True

def _render_master_peak_plot(h5file, dbfilepath, h5readpath, output_prefix, dataset_names, cmz, rts, spectra, h5fullprofile, plot_width, top_plot_height, bottom_plot_height,
                             quantity_integrals, X_3D):

    with open('%s/master_peak_plot.html'%(output_prefix), 'w') as fspec:
        dataset_count = len(dataset_names);
        
        allowed_step = np.median(h5file[h5readpath].attrs['mean_peak_width'])/180;

        #dataset_names  x1 for big plot
        #rts x2 for big plot
        
        printlog('Preparing Max Profile...');
        
        all_rts_set = h5fullprofile + 'crt';
        if not (all_rts_set in h5file):
            printlog('Error! crt not found in [%s]%s ! Skipping...'%(dbfilepath, h5fullprofile))
            return
        
        crt = h5file[all_rts_set]; #x for top plot continuous profile
        
        fy = np.zeros(crt.shape, dtype = np.float64); #y for top plot continuous profile

        for dataset_name in dataset_names:
            peaks_set = h5fullprofile+'%s/sp'%dataset_name;
            printlog(dataset_name)
            if not (peaks_set in h5file):
                printlog('Error! %s/sp not found in [%s]%s ! Skipping...'%(dataset_name, dbfilepath, h5fullprofile))
                return
            peaks = h5file[peaks_set];
            peaks = np.sum(peaks, axis = 1);
            fy = np.maximum(fy, peaks);
        
        crt = np.array(crt) / 60.0;
        
        y = np.max(quantity_integrals, axis = 0);
        
        y_max = np.max(y);
        fy_max = np.max(fy);
        if (y_max > 0) and (fy_max > 0):
            fy = np.multiply(fy, y_max/fy_max);
        
        rts = np.array(rts)/60;
        x = rts;
        minx = np.min(rts);
        maxx = np.max(rts);

        fx = crt;
        fminx = np.min(crt);
        fmaxx = np.max(crt);
        
        y0 = np.zeros((len(rts), ), dtype = np.float64);
        
        top_plot = _make_top_rt_plot(x, allowed_step, y, y0, minx, maxx, fx, fy, fminx, fmaxx, 'RT Integral profile, linear scale', False, plot_width = plot_width, plot_height = top_plot_height);
        
        #Bottom plot
        y = np.array(quantity_integrals);
        bottom_plot = _make_bottom_rt_plot(x, allowed_step, y, minx, maxx, dataset_count, dataset_names, 'Sample RT profiles, log scale, median-subtracted', plot_width = plot_width, plot_height = bottom_plot_height);

        #try synchronize
        bottom_plot.x_range = top_plot.x_range;
        
        script, div = components(gridplot([[top_plot], [bottom_plot]]));
        
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
                                


def _make_top_plot(x, dx, y, y0, minx, maxx, title, is_log = False, plot_width = 900, plot_height = 300):
    
    dx = dx / 2.0;
    vy = y;
    if is_log:
        y = y + 1.0;
        y0 = y0 + 1.0;
        
    source = ColumnDataSource(data=dict(
       top =  list(y),
       bottom =  list(y0),
       left =  list(x - dx),
       right = list(x + dx),
       desc = list(x),
       intens = list(vy),
       peakno = range(1, len(x)+1)
    ))
   
    hover = HoverTool(tooltips=[
        ("Peak No", "@peakno"),
        ("m/z (Da)", "@desc"),
        ("Integral", "@intens"),
    ])
    
    if is_log:
        s = figure(plot_width = plot_width, 
                   plot_height = plot_height, 
                   title = title, 
                   tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
                   toolbar_location = "above",
                   toolbar_sticky = False,
                   x_range = (minx, maxx),
                   y_axis_location = "right",
                   y_axis_type = "log"
                   );
    else:
        s = figure(plot_width = plot_width, 
                   plot_height = plot_height, 
                   title = title, 
                   tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
                   toolbar_location = "above",
                   toolbar_sticky = False,
                   x_range = (minx, maxx),
                   y_axis_location = "right"
                   );

    s.add_tools(hover);

    s.quad(top = 'top', bottom = 'bottom', left = 'left',
       right = 'right', color = "navy", source = source)
                    
    return s

def _make_bottom_plot(subpeaks, cmz_x, minx, maxx, dataset_count, dataset_names, title, is_log = False, plot_width = 900, plot_height = 400, max_y = -1):
    sample = [];
    color = [];
    
    sample_no = np.zeros((subpeaks.shape[1], subpeaks.shape[0]), dtype = np.int32);
    sample_n = np.arange(subpeaks.shape[0], dtype = np.int32);
    sample_no[:, :] = sample_n[:];
    sample_no = np.transpose(sample_no).flatten();
    
    top = np.add(sample_no, 1).flatten();
    bottom = sample_no.flatten();

    mz = np.zeros(subpeaks.shape, dtype = np.float64);
    mz[:,:] = cmz_x[:];
    mz = mz.flatten();
    
    left = np.subtract(mz, 0.5).flatten();
    right = np.add(mz, 0.5).flatten();

    intens = subpeaks.flatten();
    
    mask = intens > 0.0;
    
    sample_no = sample_no[mask];
    top = top[mask];
    bottom = bottom[mask];
    mz = mz[mask];
    left = left[mask];
    right = right[mask];
    intens = intens[mask];
    
    min_y = np.min(intens);
    if max_y < 0:
        max_y = np.max(intens);
    
    if is_log:
        if min_y == 0.0:
            min_y += 1.0;
            max_y += 1.0;
            intens += 1.0;
        bb = np.log(max_y) - np.log(min_y);
        if bb == 0.0:
            cvl = np.full(intens.shape, 255, dtype = np.float64);    
        else:
            cvl = ((np.log(intens) - np.log(min_y))/bb)*255;
    else:
        bb = max_y - min_y;
        if bb == 0.0:
            cvl = np.full(intens.shape, 255, dtype = np.float64);
        else:
            cvl = ((intens - min_y)/bb)*255;
        
    #intens = intens.tolist();    
    
    sample_no = sample_no.tolist();    
    
    for j in range(len(sample_no)):
        sample.append(dataset_names[sample_no[j]].lstrip('/'));
        ii = min(int(cvl[j]), 255);
        color.append(Inferno256[ii]);
            
        
    source = ColumnDataSource(data=dict(
       top = top.tolist(),
       bottom = bottom.tolist(),
       left = left.tolist(),
       right = right.tolist(),
       sample = sample,
       sample_no = sample_no,
       mz = mz.tolist(),
       intens = intens.tolist(),
       color = color,
    ))
    
       
    hover = HoverTool(tooltips=[
        ("Sample No", "@sample_no"),
        ("Sample", "@sample"),
        ("m/z (Da)", "@mz"),
        ("Integral", "@intens"),
    ])
    
    if is_log:
        color_mapper = LinearColorMapper(palette = "Inferno256", low = np.log(min_y), high = np.log(max_y));
    else:
        color_mapper = LinearColorMapper(palette = "Inferno256", low = min_y, high = max_y);
    ticker = BasicTicker();

    s = figure(plot_width = plot_width, 
               plot_height = plot_height, 
               title = title, 
               x_range = (minx, maxx),
               y_range = (0, dataset_count),
               tools = "pan,wheel_zoom,box_zoom,undo,redo,reset", 
               toolbar_location = "above",
               toolbar_sticky = False,
               y_axis_location = "right",
               background_fill_color = "black");
    
    s.xgrid.grid_line_color = None;
    s.ygrid.grid_line_color = None;
    s.add_tools(hover);
    
    s.quad(top = 'top', bottom = 'bottom', left = 'left',
       right = 'right', color = 'color', source = source);        
    
    color_bar = ColorBar(color_mapper = color_mapper, 
                         ticker = ticker, 
                         label_standoff = 12, 
                         border_line_color = None, 
                         location = (0, 0),
                         orientation = "horizontal")        

    s.add_layout(color_bar, 'below');
   
    return s




def generate_merged_spec_report(fspec, h5file, dbfilepath, h5readpath, output_prefix, dataset_names, cmz, rts, spectra, 
                                                                h5fullprofile, plot_width, top_plot_height, bottom_plot_height, quantity_integrals, X_3D,
                                                                group_variance, start_i, extent):
                                                                    

    original_rt_index = int(group_variance[start_i, 0]);
    
    dataset_count = len(dataset_names);
    cmz_x = np.array(cmz);
    minx = np.min(cmz);
    maxx = np.max(cmz);

    tops = [];
    
    bottoms = [];
    
    mpeaks_set = h5readpath + 'merged_X_3D';
    if not (mpeaks_set in h5file):
        printlog('Error! merged_X_3D not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
        return
    
    mX_3D = h5file[mpeaks_set];
    
    subpeaks = mX_3D[:, :, original_rt_index];

    max_y = np.max(subpeaks);
    
    y = np.sum(subpeaks, axis = 0)        
    
    total_scale = 100.0 / np.max(y);
    
    y = y * total_scale;
    
    v = y[:] > 0.0;
    y = y[v];
    x = cmz_x[v];
    
    y0 = np.zeros(y.shape, dtype = np.float64);
                        
    top_plot = _make_top_plot(x, 1.0, y, y0, minx, maxx, 'Integral profile, linear scale, Merged original rt %.2f min.'%(group_variance[start_i, 1] / 60), False, plot_width = plot_width, plot_height = top_plot_height);
        
    tops.append(top_plot)
    
    
    minx = int(np.floor(minx));
    maxx = int(np.ceil(maxx));
                        
    bottom_plot = _make_bottom_plot(subpeaks, cmz_x, minx, maxx, dataset_count, dataset_names, 'Sample profiles, log scale, Merged original rt %.2f min.'%(group_variance[start_i, 1] / 60), 
                                        True, plot_width = plot_width, plot_height = bottom_plot_height, max_y = max_y);
                                        
    bottoms.append(bottom_plot)
    
    ss = X_3D[:, :, start_i:extent + 1];
    
    subpeaks = np.sum(ss, axis = 2);
    
    max_y = np.max(subpeaks);
        
    y = np.sum(subpeaks, axis = 0) * total_scale;
        
    v = y[:] > 0.0;
    y = y[v];
    x = cmz_x[v];
            
    y0 = np.zeros(y.shape, dtype = np.float64);
                        
    top_plot = _make_top_plot(x, 1.0, y, y0, minx, maxx, 'Integral profile, linear scale, rt %.2f min. Reconstructed.'%(group_variance[start_i, 1] / 60), False, plot_width = plot_width, plot_height = top_plot_height);
        
    tops.append(top_plot)
                        
    
        #Bottom plot
    minx = int(np.floor(minx));
    maxx = int(np.ceil(maxx));
                        
    bottom_plot = _make_bottom_plot(subpeaks, cmz_x, minx, maxx, dataset_count, dataset_names, 'Sample profiles, log scale, rt %.2f min. Reconstructed.'%(group_variance[start_i, 1] / 60), 
                                        True, plot_width = plot_width, plot_height = bottom_plot_height, max_y = max_y * 20);
                                        
    bottoms.append(bottom_plot)    
    
    
    
    
    for i in range(start_i, extent + 1):
                    
        #y = spectra[i];
        
        subpeaks = X_3D[:, :, i];                
        
        y = np.sum(subpeaks, axis = 0) * total_scale;
        
        v = y[:] > 0.0;
        y = y[v];
        x = cmz_x[v];
            
        #maxy = np.max(y);
        #if maxy > 0.0:
        #    y = np.divide(y, maxy) * 100.0;
    
        y0 = np.zeros(y.shape, dtype = np.float64);
                        
        top_plot = _make_top_plot(x, 1.0, y, y0, minx, maxx, 'Integral profile for peak %s, linear scale, rt %.2f min. (%s%%) '%(i + 1, group_variance[i, 1] / 60, int(group_variance[i, 7])), False, plot_width = plot_width, plot_height = top_plot_height);
        
        tops.append(top_plot)
                        
    
        #Bottom plot
        minx = int(np.floor(minx));
        maxx = int(np.ceil(maxx));
                        
        bottom_plot = _make_bottom_plot(subpeaks, cmz_x, minx, maxx, dataset_count, dataset_names, 'Sample profile for peak %s, log scale, rt %.2f min. (%s%%)'%(i + 1, group_variance[i, 1] / 60, int(group_variance[i, 7])), 
                                        True, plot_width = plot_width, plot_height = bottom_plot_height, max_y = max_y * 20);
                                        
        bottoms.append(bottom_plot)
    
    #try synchronize
    for top_plot in tops:
        top_plot.x_range = tops[0].x_range;
        top_plot.y_range = tops[0].y_range;
        
    for bottom_plot in bottoms:
        bottom_plot.x_range = tops[0].x_range;
        bottom_plot.y_range = bottoms[0].y_range;
                        
    combined = tops + bottoms
    v = [];
    for c in combined:
        v.append([c])
        
    script, div = components(gridplot(v));
                    
                    
    fspec.write(    '\n'.join([
                                    '<!DOCTYPE html>',
                                    '<html lang="en">',
                                    '    <head>',
                                    '        <meta charset="utf-8">',
                                    '        <title>Spectrums for Merged rt peaks %s - %s</title>'%(start_i + 1, extent + 1),
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





def export_HTML_view_to_file(dbfilepath, h5readpath, output_prefix, h5fullprofile, plot_width = 900, top_plot_height = 300, bottom_plot_height = 400):            
    printlog('Exporting HTML view from [%s]%s to %s...'%(dbfilepath, h5readpath, output_prefix));
    
    with h5py.File(dbfilepath, 'r') as h5file:
        
        quantity_integral_set = h5readpath + 'quantity_integrals';
        if not (quantity_integral_set in h5file):
            printlog('Error! quantity_integrals not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        grouped_dataset_names_set = h5readpath + 'dataset_names';
        if not (grouped_dataset_names_set in h5file):
            printlog('Error! dataset_names not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        utf_8_set = h5readpath + 'utf_8';
        if not (utf_8_set in h5file):
            printlog('Error! utf_8 not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return
        
        # TODO: replace it back
        peaks_set = h5readpath + 'X_3D';
        #peaks_set = h5readpath + 'merged_X_3D';
        if not (peaks_set in h5file):
            printlog('Error! X_3D not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        spectra_set = h5readpath + 'integral_MS_spectra';
        if not (spectra_set in h5file):
            printlog('Error! integral_MS_spectra not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return

        cmz_set = h5readpath + 'grouped_cmz';
        if not (cmz_set in h5file):
            printlog('Error! grouped_cmz not found in [%s]%s ! Skipping...'%(dbfilepath, h5readpath))
            return
        
        # TODO: replace it back
        rts_set = h5readpath + 'grouped_rts';
        #rts_set = h5readpath + 'merged_grouped_rts';
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
            
            
            
        if not os.path.exists(output_prefix):
            os.makedirs(output_prefix);

        rel_integrals = h5file[rel_integral_set];
        order = np.array(h5file[order_set]);

        max_rel_int = np.max(rel_integrals, axis = 0);
        
        all_order = np.max(order);

        order[order == 0] = all_order + 1;
        
        best_order = np.min(order, axis = 0);


        quantity_integrals = h5file[quantity_integral_set]; #y for big plot 
        grouped_dataset_names = h5file[grouped_dataset_names_set];
        utf_8 = h5file[utf_8_set];
        dataset_names = h5read_strings(grouped_dataset_names, utf_8);
        
        X_3D = h5file[peaks_set];
        
        #(len(procdataset_names),n_cmz, n_crt)

        #cmz_refs  = h5file[cmz_refs_set];
        #crt_refs = h5file[crt_refs_set];
        #dataset_refs = h5file[dataset_refs_set];

        spectra = h5file[spectra_set];    
            
        #peaks = h5file[peaks_set];    
       
        cmz = h5file[cmz_set];    
        
        rts = h5file[rts_set];
        rts_count = rts.shape[0];   
        dataset_count = len(dataset_names);
        
        with open('%s/index.html'%output_prefix, 'w') as fout:
            fout.write('\n'.join([
            '<!DOCTYPE html>',
            '<html>',
            '<frameset cols="15%,85%">',
            '<frame src="rt_peaks.html">',
            '<frame src="master_peak_plot.html" name="MSSpectrum">',
            '</frameset>',
            '</html>',
            ]));

        if not os.path.exists('%s/spectra'%output_prefix):
            os.makedirs('%s/spectra'%output_prefix);
        previous_rt = -1;    
        with open('%s/rt_peaks.html'%output_prefix, 'w') as fout:
            rt_peaks = [];
            for i in range(rts_count):
                printlog('RT peak: %s of %s'%(i + 1, rts_count));
                rt = rts[i];
                
                #subpeaks = peaks[crt_refs[i]].reshape(6, -1);                
                
                maxv = np.max(quantity_integrals[:, i]);
                
                                
                if deconvolved:

                    if previous_rt != int(group_variance[i, 0]):
                        previous_rt = int(group_variance[i, 0]);
                        extent = i;
                        for j in range(i+1, rts_count):
                            if int(group_variance[j, 0]) == previous_rt:
                                extent = j;
                            else:
                                break;
                                
                        if extent > i:       
                        
                            rt_peaks.append('\n'.join([
                                '<tr><td>',
                                '<a href="spectra/mspec_%s-%s_merged.html" target="MSSpectrum">Original %.2f min. (Merged peaks %s-%s) </a>'%(i + 1, extent + 1, rt/60, i + 1, extent + 1),
                                #'Mean Original Integral: %.1f'%group_variance[i, 5],
                                '</td></tr>',
                                ]));
                                
                            with open('%s/spectra/mspec_%s-%s_merged.html'%(output_prefix, i + 1, extent + 1), 'w') as fspec:
                                generate_merged_spec_report(fspec, h5file, dbfilepath, h5readpath, output_prefix, dataset_names, cmz, rts, spectra, 
                                                                h5fullprofile, plot_width, top_plot_height, bottom_plot_height, quantity_integrals, X_3D,
                                                                group_variance, i, extent);

                    
                    rt_peaks.append('\n'.join([
                        '<tr><td>%s. '%(i+1),
                        '<a href="spectra/spec_%s.html" target="MSSpectrum">%.2f min. deconv. (%s%%)</a><br>'%(i + 1, rt/60, int(group_variance[i, 7])),
                        'Max Rel. Integral: %.3f<BR>'%max_rel_int[i],
                        'Best Order: %s'%best_order[i],
                        '</td></tr>',
                        ]));
                
                else:    
                
                    rt_peaks.append('\n'.join([
                        '<tr><td>%s. '%(i+1),
                        '<a href="spectra/spec_%s.html" target="MSSpectrum">%.2f min.</a><br>'%(i + 1, rt/60),
                        'Max Rel. Integral: %.3f<BR>'%max_rel_int[i],
                        'Best Order: %s'%best_order[i],
                        '</td></tr>',
                        ]));

                with open('%s/spectra/spec_%s.html'%(output_prefix, i + 1), 'w') as fspec:

                    cmz_x = np.array(cmz);
                    minx = np.min(cmz);
                    maxx = np.max(cmz);
                    
                    y = spectra[i];
                    
                    v = y[:] > 0.0;
                    y = y[v];
                    x = cmz_x[v];
        
                    maxy = np.max(y);
                    if maxy > 0.0:
                        y = np.divide(y, maxy) * 100.0;

                    y0 = np.zeros(y.shape, dtype = np.float64);
                    
                    
                    top_plot = _make_top_plot(x, 1.0, y, y0, minx, maxx, 'Integral profile, linear scale, scaled to 100 max', False, plot_width = plot_width, plot_height = top_plot_height);
                    
                    #Bottom plot
                    minx = int(np.floor(minx));
                    maxx = int(np.ceil(maxx));
                    
                    subpeaks = X_3D[:, :, i];
                    
                    bottom_plot = _make_bottom_plot(subpeaks, cmz_x, minx, maxx, dataset_count, dataset_names, 'Sample profiles, log scale', True, plot_width = plot_width, plot_height = bottom_plot_height);

                    #try synchronize
                    bottom_plot.x_range = top_plot.x_range;
                    
                    script, div = components(gridplot([[top_plot], [bottom_plot]]));
                    
                    
                    fspec.write(    '\n'.join([
                                    '<!DOCTYPE html>',
                                    '<html lang="en">',
                                    '    <head>',
                                    '        <meta charset="utf-8">',
                                    '        <title>Spectrum for rt peak %s</title>'%(i + 1),
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
                                           
            if _generate_metatable(h5file, dbfilepath, h5readpath, output_prefix, dataset_names):
                mt = '    <tr><td><a href="metadata.html" target="MSSpectrum">MetaData Table</a></td></tr>';            
            else:
                mt = '';

            fout.write('\n'.join([
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Retention time peaks</title>',
            '</head>',
            '<body>',
            '    <table border=1>',
            '    <tr><th>Overall Plots</th></tr>',
            '    <tr><td><a href="master_peak_plot.html" target="MSSpectrum">Master Peak Plot</a></td></tr>',
            mt,
            '    <tr><th>Individual Retention time peaks</th></tr>',
            '    %s'%'\n'.join(rt_peaks),
            '    </table>',
            '</body>',
            '</html>',
            ]));
            
        
        printlog('Making master peak plot...');
        _render_master_peak_plot(h5file, dbfilepath, h5readpath, output_prefix, dataset_names, cmz, rts, spectra, h5fullprofile, plot_width, top_plot_height, bottom_plot_height,
                                 quantity_integrals, X_3D);
            
        printlog('Done')        
        
    

def do_report(dbfilepath, params = {'h5readpath':'/spproc2D_peakdetect', 
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
    params['h5fullprofile'] = h5Base.correct_h5path(params['h5fullprofile'])
    dbfilepath = os.path.abspath(dbfilepath);
    
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
        
    export_HTML_view_to_file(dbfilepath, params['h5readpath'], output_prefix, params['h5fullprofile'],
                             params['plot_width'], params['top_plot_height'], params['bottom_plot_height']);

                    
    return
        

if __name__ == "__main__": 
    tic();
    settings=OptionsHolder(__doc__, Reporting_options);
    settings.description='Generating HTML report';
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
    printlog(settings.format_parameters());
   
    do_report(settings.parameters['dbfilename'],
                     params = settings.parameters['params'])
    
    printlog('\nFinished on %s in'%(time.strftime("%a, %d %b %Y at %H:%M:%S")));   
    toc();
    printlog(settings.description_epilog);
    stop_log();
from bokeh.models import ColumnDataSource, Slider, HoverTool, CustomJS, BoxSelectTool, Range1d, TextInput
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import row, column

import os, sys
import numpy as np
from lttb.lttb.lttb import largest_triangle_three_buckets
import proc.io.manageh5db as mh5


def down_sample(data=None, limits=(0,3000), npoints=100):
    newx = []
    newy = []
    for isample in range(len(data['x'])):
        boundidx = (data['x'][isample] >= limits[0]) & (data['x'][isample] <= limits[1])
        boundX = data['x'][isample][boundidx]
        boundY = data['y'][isample][boundidx]

        if (npoints) >= len(boundX):
            downdata = list(zip(boundX, boundY))
        else:
            downdata = largest_triangle_three_buckets(list(zip(boundX, boundY)), (npoints))

        newxtmp = []
        newytmp = []
        for x, y in downdata:
            newxtmp.append(x)
            newytmp.append(y)
        newx.append(newxtmp)
        newy.append(newytmp)

    newdata = {'x': newx, 'y': newy, 'id': data['id'], 'color': data['color']}
    return newdata

def colorgenerator(N):
    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100
    colors = ["#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(np.floor(50 + 2 * x), np.floor(30 + 2 * y))]
    return colors

def get_data(dbfilepath, h5readpath='sp2D'):
    if h5readpath[0] != '/':
        h5readpath = '/'.join(['', 'sp2D'])

    if os.path.isfile(dbfilepath):
        datasets = mh5.get_dataset_names(dbfilepath, pathinh5=h5readpath)
        if not datasets:
            print(dbfilepath + ' database file doesn''t contain any MSI datasets')
            return
    else:
        print(str(dbfilepath) + ' database file is not found')
        return

    sizesp = mh5.load_dataset(dbfilepath, os.path.join(h5readpath, 'sizesp'))
    tics = np.zeros((sizesp[0], sizesp[2]))
    crt = mh5.load_dataset(dbfilepath, os.path.join(h5readpath, 'crt'))
    j = -1
    dataidx = np.array([])
    for datasetid in datasets:
        j = j + 1
        try:
            sp = mh5.load_dataset(dbfilepath, ''.join([h5readpath, datasetid, '/sp']))
            tics[:, j] = np.sum(sp, axis=1)
            dataidx = np.append(dataidx, j)
        except:
            print(os.path.basename(datasetid) + ": Failed to readin")
            pass
    dataidx = dataidx.astype(int)
    datasets = list(map(datasets.__getitem__, (dataidx)))
    tics = tics[:, dataidx]
    nrows, ncols = tics.shape
    sp = {'x': [], 'y': [], 'id': [], 'color': []}
    for i in range(ncols):
        sp['x'].append(crt)
        sp['y'].append(tics[:, i])
        sp['id'].append(datasets[i])
    sp['color'] = colorgenerator(ncols)
    return sp

def x_range_change_cb(attr, old, new):
    new_range = (plot.x_range.start, plot.x_range.end)
    if None in new_range:
        return
    new_data = down_sample(data=data, npoints=screenwidth, limits=new_range)
    source.data = ColumnDataSource(data=new_data).data
    print('change detected!')


# get paths from argument list
dbfilepath = '/Users/Dieter/Desktop/MSHub_final/users/dgalea14/projects/default_43/jobs/job_174/sampleGCMS.h5'
h5readpath = 'sp2D'


# define defaults
screenwidth = 800
screenheight = 600
initrange = (0,3000)
figtitle = 'Total Ion Chromatograms'

# get data
data = get_data(dbfilepath= dbfilepath,
          h5readpath=h5readpath)

# down-sample data
subdata = down_sample(data=data, npoints=screenwidth, limits=initrange)
source = ColumnDataSource(subdata)

# plot the data
plot = figure(x_range=initrange, plot_width=screenwidth, plot_height=screenheight, y_axis_label='Intensity',
              x_axis_label='Time(s)', title=figtitle, tools="pan,wheel_zoom, box_zoom,reset,save")

plot.multi_line(xs='x', ys='y', line_color='color', line_width=1,
                hover_line_color='color', hover_line_alpha=1.0, source=source)

plot.x_range.on_change('start', x_range_change_cb)
plot.x_range.on_change('end', x_range_change_cb)

# add to current document being served by bokeh server
curdoc().add_root(row(plot))
curdoc().title = "Testing"




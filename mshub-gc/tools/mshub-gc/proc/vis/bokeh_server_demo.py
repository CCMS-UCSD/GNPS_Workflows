from tornado.ioloop import IOLoop

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, HoverTool, CustomJS, BoxSelectTool, Range1d, TextInput
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
import numpy as np
import os
import proc.io.manageh5db as mh5
from lttb.lttb.lttb import largest_triangle_three_buckets

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
        datasets = mh5.get_dataset_names(dbfilepath, dataset_names=[], pathinh5=h5readpath)
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

io_loop=IOLoop.current()

screenwidth = 800
screenheight = 600
initrange = (0,3000)

figtitle = 'Total Ion Chromatograms'
# data = view_tics(dbfilepath='/Users/Dieter/Desktop/MSHub_final/users/dgalea14/projects/default_43/jobs/job_174/sampleGCMS.h5',
#           method='bokeh', params={'h5readpath':'sp2D', 'outputfile':'', 'inline':''})
data = get_data(dbfilepath='/Users/Dieter/Desktop/MSHub_final/users/dgalea14/projects/default_43/jobs/job_174/sampleGCMS.h5',
          h5readpath='sp2D')

subdata = down_sample(data=data, npoints=screenwidth, limits=initrange)
source = ColumnDataSource(subdata)

plot = figure(x_range=initrange, plot_width=screenwidth, plot_height=screenheight, y_axis_label='Intensity',
              x_axis_label='Time(s)', title=figtitle, tools="pan,wheel_zoom, hover, box_zoom,reset,save")

plot.toolbar.active_inspect = None

plot.multi_line(xs='x', ys='y', line_color='color', line_width=1,
                hover_line_color='color', hover_line_alpha=1.0, source=source)

def modify_doc(doc):

    def x_range_change_cb(attr, old, new):
        new_range = (plot.x_range.start, plot.x_range.end)
        if None in new_range:
            return

        new_data = down_sample(data=data, npoints=screenwidth, limits=new_range)
        source.data = ColumnDataSource(data=new_data).data

        print('change detected!')

    plot.x_range.on_change('start', x_range_change_cb)
    plot.x_range.on_change('end', x_range_change_cb)
    doc.add_root(column(plot))

server = Server({'/': Application(FunctionHandler(modify_doc))}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    io_loop.add_callback(server.show, "/")
    io_loop.start()
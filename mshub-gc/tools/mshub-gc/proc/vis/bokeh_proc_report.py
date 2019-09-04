from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.plotting import figure
import numpy as np
import proc.io.manageh5db as mh5
from proc.vis.lttb.lttb.lttb import largest_triangle_three_buckets
import os
import time

def down_sample(data=None, limits=(0,3000), npoints=100, prevdata=None, newlabel=None):
    newx = []
    newy = []

    # x is constant between samples so let's take the first one rather than doing it for all samples (this makes it
    # twice as fast)
    boundidx = (data['x'][0] >= limits[0]) & (data['x'][0] <= limits[1])
    boundX = data['x'][0][boundidx]

    for isample in range(len(data['x'])):
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

    if prevdata:
        newdata = prevdata
        newdata[newlabel['y']] = newy
        newdata[newlabel['x']] = newx
    else:
        if newlabel:
            newdata = {newlabel['x']: newx, newlabel['y']: newy, 'id': data['id'], 'color': data['color']}
        else:
            newdata = {'x': newx, 'y': newy, 'id': data['id'], 'color': data['color']}
    return newdata

def colorgenerator(N):
    """ Generate N random colors """
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


def draw_dashboard(plot_types=None, h5path='', outputdir=''):

    # let's define the defaults
    screenwidth = 500
    screenheight = 350
    x_initrange = (185,2820)     # TODO - get the minimum and maximum from the spectra
    y_initrange = (0, 34000000)
    y_axis_label = 'Intensity (AU)'
    x_axis_label = 'Time (s)'
    TOOLS = "pan,hover,box_zoom,wheel_zoom,reset,save"
    mergeddata = {}
    titlemap = {'sp2D': 'Intra-sample alignment',
                'spproc2D': 'Noise filtering and baseline correction',
                'spal2D': 'Inter-sample alignment'}

    for ip, iplot in enumerate(plot_types):
        data = get_data(dbfilepath=h5path, h5readpath=iplot)
        subdata = down_sample(data=data, npoints=screenwidth, limits=x_initrange, newlabel={'y': '_'.join(['y', iplot]),
                                                                                          'x': '_'.join(['x', iplot])})
        if ip == 0:
            firstplot = iplot
            mergeddata = subdata
        else:
            for key in subdata:
                if key not in ['color', 'id']:
                    mergeddata[key] = subdata[key]
                else:
                    continue

    source = ColumnDataSource(mergeddata)
    plots = []

    ########################################## SAMPLE LIST ##########################################
    columns = [TableColumn(field="id", title="sample id")]
    sample_table = DataTable(source=source, columns=columns, width=300, height=700)

    for ip, iplot in enumerate(plot_types):
        if ip == 0:
            x_range = x_initrange
            y_range = y_initrange
        else:
            x_range = plots[0].x_range
            y_range = plots[0].y_range

        plot = figure(x_range=x_range,
                      y_range=y_range,
                      plot_width=screenwidth,
                      plot_height=screenheight,
                      y_axis_label=y_axis_label,
                      x_axis_label=x_axis_label,
                      title=titlemap[iplot],
                      tools=TOOLS)

        plot.toolbar.active_inspect = None

        plot.multi_line(xs='_'.join(['x', iplot]),
                        ys='_'.join(['y', iplot]),
                        line_color='color',
                        line_width=1,
                        hover_line_color='color',
                        hover_line_alpha=1.0,
                        nonselection_line_color='grey',
                        nonselection_line_alpha=0.01,
                        source=source)
        plots.append(plot)

    gp = gridplot(children=plots, ncols=2, toolbar_options={'logo': None})
    script, div = components((sample_table, gp))

    with open(os.path.join(outputdir,'proc_report.html'), 'w') as writefile:
        writefile.write("<html>\n"
                        "<head>\n"
                        "<link href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css' rel='stylesheet'>\n"
                        "<link href='http://cdn.pydata.org/bokeh/release/bokeh-0.12.6.min.css' rel='stylesheet' type='text/css'>\n"
                        "<link href='http://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.6.min.css' rel='stylesheet' type='text/css'>\n"
                        "<script src='http://cdn.pydata.org/bokeh/release/bokeh-0.12.6.min.js'></script>\n"
                        "<script src='http://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.6.min.js'></script>\n")

        writefile.write(script)
        writefile.write('\n')
        writefile.write("</head>\n")
        writefile.write("<body>\n")
        writefile.write("<div class='row'>\n")
        writefile.write("<div class='col-md-3'>\n")
        writefile.write(div[0])
        writefile.write("</div>")
        writefile.write("<div class='col-md-9'>\n")
        writefile.write(div[1])
        writefile.write("</div>")
        writefile.write("</div>")
        writefile.write("</body>\n")
        writefile.write("</html>\n")


if __name__ == "__main__":
    draw_dashboard(plot_types=['sp2D', 'spproc2D', 'spal2D'],
                   h5path='/Users/Dieter/Desktop/MSHub_final/test_all.h5',
                   outputdir='')



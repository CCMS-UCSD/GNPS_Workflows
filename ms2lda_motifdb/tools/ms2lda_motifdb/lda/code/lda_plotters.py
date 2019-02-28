# -*- coding: utf-8 -*-

import plotly as plotly
from plotly.graph_objs import *
import networkx as nx
import json
import pickle
import numpy as np
from networkx.readwrite import json_graph




# Some useful plotting code (uses plotly)
# Should put this into a separate file
class VariationalLDAPlotter(object):
  def __init__(self,v_lda):
    plotly.offline.init_notebook_mode()
    self.v_lda = v_lda

  def bar_alpha(self):
    K = len(self.v_lda.alpha)
    data = []
    data.append(
      Bar(
        x = range(K),
        y = self.v_lda.alpha,
        )
      )
    plotly.offline.iplot({'data':data})
  def mean_gamma(self):
    K = len(self.v_lda.alpha)
    data = []
    data.append(
      Bar(
        x = range(K),
        y = self.v_lda.gamma_matrix.mean(axis=0),
        )
      )
    plotly.offline.iplot({'data':data})




  def plot_document_colour_one_topic(self,doc,topic,precursor_mass = None,intensity_thresh = 0,show_losses = False,title = None,xlim = None):
    eth = self.v_lda.get_expect_theta()
    pos = self.v_lda.doc_index[doc]

    topic_colour = ('rgb(255,0,0)')
    background_colour = ('rgba(50,50,50,0.3)') 
    precursor_colour = ('rgb(0,0,255)')

    data = []


    max_mass = 0.0
    max_intensity = 0.0
    for word in self.v_lda.corpus[doc]:
        word_type = word.split('_')[0]
        intensity = self.v_lda.corpus[doc][word]
        if intensity > max_intensity:
            max_intensity = intensity
        topic_contribution = self.v_lda.phi_matrix[doc][word][topic]
        if word_type == 'fragment':
            mass = float(word.split('_')[1])
            if mass > max_mass:
                max_mass = mass
            data.append(
                Scatter(
                    x = [mass,mass],
                    y = [0,topic_contribution*intensity],
                    mode = 'lines',
                    line = dict(
                        color = topic_colour,
                        ),
                    showlegend = False,
                )
            )
            data.append(
                Scatter(
                    x = [mass,mass],
                    y = [topic_contribution*intensity,intensity],
                    mode = 'lines',
                    line = dict(
                        color = background_colour,
                        ),
                    showlegend = False,
                )
            )
        else:
            if not precursor_mass == None and show_losses:
                # This is a fragment
                yval = 0.9*intensity
                mass = float(word.split('_')[1])
                xvals = [precursor_mass - mass,precursor_mass - mass + topic_contribution*mass]
                data.append(
                    Scatter(
                        x = xvals,
                        y = [yval,yval],
                        mode = 'lines',
                        line = dict(
                            color = topic_colour,
                            ),
                        showlegend = False,
                        text = word,
                        )
                    )
                xvals = [precursor_mass - mass + topic_contribution*mass,precursor_mass]
                data.append(
                    Scatter(
                        x = xvals,
                        y = [yval,yval],
                        mode = 'lines',
                        line = dict(
                            color = background_colour,
                            ),
                        showlegend = False,
                        )
                    )
                data.append(
                    Scatter(
                        x = [precursor_mass,precursor_mass],
                        y = [0,max_intensity],
                        mode = 'lines',
                        line = dict(
                            color = precursor_colour,
                            ),
                        showlegend = False,
                        )
                    )

    if precursor_mass == None:
        precursor_mass = max_mass
    if title == None:
        title = str(doc)
    if xlim == None:
        xlim = [0,precursor_mass+10]
    layout = Layout(
        title = title,
        xaxis = dict(
            range = xlim,
            )
        )
    plotly.offline.iplot({'data':data,'layout':layout})


  # Colour by the top N topics in the document
  def plot_document_topic_colour(self,doc,precursor_mass = None,topn = 4,intensity_thresh = 0,show_losses = False,title = None,xlim=None):
    eth = self.v_lda.get_expect_theta()
    pos = self.v_lda.doc_index[doc]
    tp = []
    # Find the highest probability topics
    for i,p in enumerate(eth[pos,:]):
        tp.append((i,p))
    tp = sorted(tp,key=lambda x:x[1],reverse=True)
    topics_to_plot = []
    for i in range(topn):
        topics_to_plot.append(tp[i][0])

    
    colours = [[255,0,0],[0,255,0],[0,0,255],[0,255,255]]
    data = []
    loss_opacity = 1.0
    top_colours = {}
    loss_colours = {}
    for i,t in enumerate(topics_to_plot):
        r = colours[i][0]
        g = colours[i][1]
        b = colours[i][2]
        top_colours[t] = ('rgb({},{},{})'.format(r,g,b))
        loss_colours[t] = ('rgba({},{},{},{})'.format(r,g,b,loss_opacity))    
    
    
    topics_plotted = [] # This will be appended to as we plot the first thing from each topic, for the legend
    max_intensity = 0.0
    for word in self.v_lda.corpus[doc]:
        if self.v_lda.corpus[doc][word] >= intensity_thresh:
            if word.startswith('fragment'):
                m = float(word.split('_')[1])
                intensity = self.v_lda.corpus[doc][word]
                if intensity >= max_intensity:
                    max_intensity = intensity
                cum = 0.0
                for t in topics_to_plot:
                    height = intensity*self.v_lda.phi_matrix[doc][word][t]
                    name = "motif_{}".format(t)
                    if t in topics_plotted:
                      s = Scatter(
                          x = [m,m],
                          y = [cum,cum+height],
                          mode = 'lines',
                          name = name,
                          marker = dict(
                              color = top_colours[t]
                          ),
                          showlegend=False,
                      )
                    else:
                      s = Scatter(
                          x = [m,m],
                          y = [cum,cum+height],
                          mode = 'lines',
                          name = name,
                          marker = dict(
                              color = top_colours[t]
                          )
                      )
                      topics_plotted.append(t)
                    cum += height
                    data.append(s)
                s = Scatter(
                    x = [m,m],
                    y = [cum,intensity],
                    mode = 'lines',
                    name = 'other topics',
                    marker = dict(
                        color = ('rgb(200,200,200)')
                    ),
                    showlegend=False,
                )
                data.append(s)
            if word.startswith('loss') and show_losses and not precursor_mass == None:
                loss_mass = float(word.split('_')[1])
                start = precursor_mass - loss_mass
                pos = start
                y = 0.9*self.v_lda.corpus[doc][word]
                for t in topics_to_plot:
                    width = loss_mass*self.v_lda.phi_matrix[doc][word][t]
                    name = "motif_{}".format(t)
                    if t in topics_plotted:
                        s = Scatter(
                            x = [pos,pos+width],
                            y = [y,y],
                            mode = 'lines',
                            name = name,
                            marker = dict(
                                color = loss_colours[t]
                            ),
                            line = dict(
                                dash = 'dash'
                            ),
                            showlegend=False,
                        )
                    else:
                        s = Scatter(
                            x = [pos,pos+width],
                            y = [y,y],
                            mode = 'lines',
                            marker = dict(
                                color = loss_colours[t]
                            ),
                            line = dict(
                                dash = 'dash'
                            ),
                            showlegend=True,
                            name = name,
                        )
                        topics_plotted.append(t)
                    pos += width
                    data.append(s)
                s = Scatter(
                    x = [pos,precursor_mass],
                    y = [y,y],
                    mode = 'lines',
                    marker = dict(
                        color = ('rgba(200,200,200,{})'.format(loss_opacity))
                    ),
                    showlegend = False
                )
                data.append(s)
            
    if not precursor_mass == None:
      s = Scatter(
          x = [precursor_mass,precursor_mass],
          y = [0,max_intensity],
          mode = 'lines',
          marker = dict(
              color = ('rgb(255,0,0)')
          ),
          showlegend = False,
      )
      data.append(s)


    if title == None:
        title = str(doc)

    if xlim == None:
        layout = Layout (
            showlegend=True,
            xaxis = dict(
                title = 'm/z',
            ),
            yaxis = dict(
                title = 'Intensity',
            ),
            title = title
        )
    else:
        layout = Layout (
            showlegend=True,
            xaxis = dict(
                title = 'm/z',
                range = xlim,
            ),
            yaxis = dict(
                title = 'Intensity',
            ),
            title = title,
        )

    plotly.offline.iplot({'data':data,'layout':layout})



class MultiFileVariationalLDAPlotter(object):
  def __init__(self,m_lda):
    plotly.offline.init_notebook_mode()
    self.m_lda = m_lda

  def multi_alpha(self,normalise=False,names=None):
    data = []
    K = self.m_lda.individual_lda[0].K
    for i,l in enumerate(self.m_lda.individual_lda):
      if normalise:
        a = l.alpha / l.alpha.sum()
      else:
        a = l.alpha
      if not names == None:
        name = names[i]
      else:
        name = 'trace {}'.format(i)
      data.append(
        Bar(
          x = range(K),
          y = a,
          name = name
          )
        )
    plotly.offline.iplot({'data':data})







class VariationalLDAPlotter_dict(object):
  def __init__(self,lda_dict):
    plotly.offline.init_notebook_mode()
    self.lda_dict = lda_dict

  def bar_alpha(self):
    K = len(self.lda_dict['alpha'])
    data = []
    data.append(
      Bar(
        x = range(K),
        y = self.lda_dict['alpha'],
        )
      )
    plotly.offline.iplot({'data':data})




  def plot_document_colour_one_topic(self,doc,topic,precursor_mass = None,intensity_thresh = 0,show_losses = False,title = None,xlim = None):

    topic_colour = ('rgb(255,0,0)')
    background_colour = ('rgba(50,50,50,0.3)') 
    precursor_colour = ('rgb(0,0,255)')

    data = []


    max_mass = 0.0
    max_intensity = 0.0
    for word in self.lda_dict['corpus'][doc]:
        word_type = word.split('_')[0]
        intensity = self.lda_dict['corpus'][doc][word]
        if intensity > max_intensity:
            max_intensity = intensity
        topic_contribution = self.lda_dict['phi'][doc][word].get(topic,0.0)


        if word_type == 'fragment':
            mass = float(word.split('_')[1])
            if mass > max_mass:
                max_mass = mass
            data.append(
                Scatter(
                    x = [mass,mass],
                    y = [0,topic_contribution*intensity],
                    mode = 'lines',
                    line = dict(
                        color = topic_colour,
                        ),
                    showlegend = False,
                )
            )
            data.append(
                Scatter(
                    x = [mass,mass],
                    y = [topic_contribution*intensity,intensity],
                    mode = 'lines',
                    line = dict(
                        color = background_colour,
                        ),
                    showlegend = False,
                )
            )
        else:
            if not precursor_mass == None and show_losses:
                # This is a fragment
                yval = 0.9*intensity
                mass = float(word.split('_')[1])
                xvals = [precursor_mass - mass,precursor_mass - mass + topic_contribution*mass]
                data.append(
                    Scatter(
                        x = xvals,
                        y = [yval,yval],
                        mode = 'lines',
                        line = dict(
                            color = topic_colour,
                            ),
                        showlegend = False,
                        text = word,
                        )
                    )
                xvals = [precursor_mass - mass + topic_contribution*mass,precursor_mass]
                data.append(
                    Scatter(
                        x = xvals,
                        y = [yval,yval],
                        mode = 'lines',
                        line = dict(
                            color = background_colour,
                            ),
                        showlegend = False,
                        )
                    )
    if not precursor_mass == None:
        data.append(
            Scatter(
                x = [precursor_mass,precursor_mass],
                y = [0,max_intensity],
                mode = 'lines',
                line = dict(
                    color = precursor_colour,
                    ),
                showlegend = False,
                )
            )

    if precursor_mass == None:
        precursor_mass = max_mass
    if title == None:
        title = str(doc)
    if xlim == None:
        xlim = [0,precursor_mass+10]
    layout = Layout(
        title = title,
        xaxis = dict(
            range = xlim,
            )
        )
    plotly.offline.iplot({'data':data,'layout':layout})


  # Colour by the top N topics in the document
  def plot_document_topic_colour(self,doc,precursor_mass = None,topn = 4,intensity_thresh = 0,show_losses = False,title = None,xlim=None):
    tp = []
    # Find the highest probability topics
    for t in self.lda_dict['theta'][doc]:
        tp.append((t,self.lda_dict['theta'][doc][t]))
    
    tp = sorted(tp,key=lambda x:x[1],reverse=True)
    topics_to_plot = []
    for i in range(min(topn,len(self.lda_dict['theta'][doc]))):
        topics_to_plot.append(tp[i][0])

    
    colours = [[255,0,0],[0,255,0],[0,0,255],[0,255,255]]
    data = []
    loss_opacity = 1.0
    top_colours = {}
    loss_colours = {}
    for i,t in enumerate(topics_to_plot):
        r = colours[i][0]
        g = colours[i][1]
        b = colours[i][2]
        top_colours[t] = ('rgb({},{},{})'.format(r,g,b))
        loss_colours[t] = ('rgba({},{},{},{})'.format(r,g,b,loss_opacity))    
    
    
    topics_plotted = [] # This will be appended to as we plot the first thing from each topic, for the legend
    max_intensity = 0.0
    for word in self.lda_dict['corpus'][doc]:
        if self.lda_dict['corpus'][doc][word] >= intensity_thresh:
            if word.startswith('fragment'):
                m = float(word.split('_')[1])
                intensity = self.lda_dict['corpus'][doc][word]
                if intensity >= max_intensity:
                    max_intensity = intensity
                cum = 0.0
                for t in topics_to_plot:
                    height = intensity*self.lda_dict['phi'][doc][word].get(t,0.0)
                    name = t
                    if t in topics_plotted:
                      s = Scatter(
                          x = [m,m],
                          y = [cum,cum+height],
                          mode = 'lines',
                          name = name + "(" + str(height) + ")",
                          marker = dict(
                              color = top_colours[t]
                          ),
                          showlegend=False,
                      )
                    else:
                      s = Scatter(
                          x = [m,m],
                          y = [cum,cum+height],
                          mode = 'lines',
                          name = name,
                          marker = dict(
                              color = top_colours[t]
                          )
                      )
                      topics_plotted.append(t)
                    cum += height
                    data.append(s)
                s = Scatter(
                    x = [m,m],
                    y = [cum,intensity],
                    mode = 'lines',
                    name = 'other topics',
                    marker = dict(
                        color = ('rgb(200,200,200)')
                    ),
                    showlegend=False,
                )
                data.append(s)
            if word.startswith('loss') and show_losses and not precursor_mass == None:
                loss_mass = float(word.split('_')[1])
                start = precursor_mass - loss_mass
                pos = start
                y = 0.9*self.v_lda.corpus[doc][word]
                for t in topics_to_plot:
                    width = loss_mass*self.v_lda.phi_matrix[doc][word][t]
                    name = "motif_{}".format(t)
                    if t in topics_plotted:
                        s = Scatter(
                            x = [pos,pos+width],
                            y = [y,y],
                            mode = 'lines',
                            name = name,
                            marker = dict(
                                color = loss_colours[t]
                            ),
                            line = dict(
                                dash = 'dash'
                            ),
                            showlegend=False,
                        )
                    else:
                        s = Scatter(
                            x = [pos,pos+width],
                            y = [y,y],
                            mode = 'lines',
                            marker = dict(
                                color = loss_colours[t]
                            ),
                            line = dict(
                                dash = 'dash'
                            ),
                            showlegend=True,
                            name = name,
                        )
                        topics_plotted.append(t)
                    pos += width
                    data.append(s)
                s = Scatter(
                    x = [pos,precursor_mass],
                    y = [y,y],
                    mode = 'lines',
                    marker = dict(
                        color = ('rgba(200,200,200,{})'.format(loss_opacity))
                    ),
                    showlegend = False
                )
                data.append(s)
            
    if not precursor_mass == None:
      s = Scatter(
          x = [precursor_mass,precursor_mass],
          y = [0,max_intensity],
          mode = 'lines',
          marker = dict(
              color = ('rgb(255,0,0)')
          ),
          showlegend = False,
      )
      data.append(s)


    if title == None:
        title = str(doc)

    if xlim == None:
        layout = Layout (
            showlegend=True,
            xaxis = dict(
                title = 'm/z',
            ),
            yaxis = dict(
                title = 'Intensity',
            ),
            title = title
        )
    else:
        layout = Layout (
            showlegend=True,
            xaxis = dict(
                title = 'm/z',
                range = xlim,
            ),
            yaxis = dict(
                title = 'Intensity',
            ),
            title = title,
        )

    plotly.offline.iplot({'data':data,'layout':layout})

  def make_graph_object(self,edge_thresh = 0.05,min_degree = 10,topic_scale_factor = 5,edge_scale_factor=5,filename = None):
    
    # Loop over the docs to find the degree of the topics
    topics = {}
    for doc in self.lda_dict['corpus']:
        for topic in self.lda_dict['theta'][doc]:
            if self.lda_dict['theta'][doc][topic] > edge_thresh:
                if topic in topics:
                    topics[topic] += 1
                else:
                    topics[topic] = 1
    to_remove = []
    for topic in topics:
        if topics[topic] < min_degree:
            to_remove.append(topic)
    for topic in to_remove:
        del topics[topic]

    print "Found {} topics".format(len(topics))

    # Add the topics to the graph
    G = nx.Graph()
    for topic in topics:
        G.add_node(topic,group=2,name=topic,
            size=topic_scale_factor * topics[topic],
            special = False, in_degree = topics[topic],
            score = 1)

    # Add the nodes to the graph
    for doc in self.lda_dict['theta']:
        # Get the compound as the name if it exists
        name = self.lda_dict['doc_metadata'][doc].get('compound',doc)
        G.add_node(doc,group=1,name = name,size=20,
            type='square',peakid = name,special=False,
            in_degree=0,score=0)
        for topic in self.lda_dict['theta'][doc]:
            G.add_edge(topic,doc,weight = edge_scale_factor*self.lda_dict['theta'][doc][topic])

    if not filename == None:
        d = json_graph.node_link_data(G) 
        json.dump(d, open(filename,'w'),indent=2)
    return G

  def write_topic_file(self,filename):
    with open(filename,'w') as f:
        for topic in self.lda_dict['beta']:
            topic_no = int(topic.split('_')[1])
            alp = self.lda_dict['alpha'][topic_no]
            f.write(topic + ' alpha = {}'.format(alp) +  '\n')
            wp = []
            for word in self.lda_dict['beta'][topic]:
                wp.append((word,self.lda_dict['beta'][topic][word]))
            wp = sorted(wp,key = lambda x: x[1], reverse=True)
            for w,p in wp:
                line = '\t{}, {:.3f}\n'.format(w,p)
                f.write(line)
            f.write('\n\n')




class MultiFileVariationalLDAPlotter_dict(object):
    def __init__(self,m_lda = None,m_lda_file = None):
        plotly.offline.init_notebook_mode()
        if m_lda == None:
            if m_lda_file == None:
                print "You must specify a file or a dictionary"
            else:
                with open(m_lda_file,'r') as f:
                    self.m_lda = pickle.load(f)
        else:
            self.m_lda = m_lda
        self.K = self.m_lda['K']
        self.n_files = len(self.m_lda['individual_lda'])

    def make_alpha_matrix(self,normalise = False):
        all_alpha = np.zeros((self.n_files,self.K),np.float)
        self.file_index = {}
        file_pos = 0
        for file in self.m_lda['individual_lda']:
            self.file_index[file] = file_pos
            all_alpha[file_pos,:] = np.array(self.m_lda['individual_lda'][file]['alpha']).copy()
            file_pos += 1
        if normalise:
            all_alpha /= all_alpha.sum(axis=1)[:,None]
        return all_alpha

    def alpha_bars(self,normalise = False):
        all_alpha = self.make_alpha_matrix(normalise = normalise)

        data = []
        for file in self.file_index:
            print file
            data.append(
                Bar(
                    x = range(self.K),
                    y = all_alpha[self.file_index[file],:],
                    name = file,
                    )
                )

        plotly.offline.iplot({'data':data})

    def alpha_pca(self,weight_thresh = 0.05,line_fact = 3,groups = None):
        from sklearn.decomposition import PCA
        all_alpha = self.make_alpha_matrix(normalise = False)
        pca = PCA(n_components = 2,whiten = True)
        pca.fit(all_alpha)
        X = pca.transform(all_alpha)

        ap = [(f,self.file_index[f]) for f in self.file_index]
        ap = sorted(ap,key = lambda x: x[1])
        reverse,_ = zip(*ap)
        reverse = list(reverse)
        data = []
        if groups == None:
            data.append(
                Scatter(
                    x = X[:,0],
                    y = X[:,1],
                    mode = 'markers',
                    marker = dict(
                        size = 20,
                        ),
                    text = reverse, 
                    showlegend = False,
                    )
                )
        else:
            for group_name in groups:
                group_pos = [i for i in range(len(reverse)) if reverse[i].startswith(group_name)]
                data.append(
                    Scatter(
                        x = X[group_pos,0],
                        y = X[group_pos,1],
                        mode = 'markers',
                        marker = dict(
                            size = 20,
                            ),
                        text = [r for r in reverse if r.startswith(group_name)],
                        name = group_name,
                    )
                )

        # TODO need proper topic names here
        for k in range(self.K):
            if np.abs(pca.components_[:,k]).sum() > weight_thresh:
                data.append(
                    Scatter(
                        x = [0,line_fact*pca.components_[0,k]],
                        y = [0,line_fact*pca.components_[1,k]],
                        name = 'Motif_{}'.format(k),
                        mode = 'lines',
                        line = dict(
                            color = ('rgba(255,0,0,0.3)'),
                            ),
                        showlegend = False,
                        )
                    )
        plotly.offline.iplot({'data':data})

        return pca

    def get_dict(self):
        return self.m_lda

def plot_document(document):
    plotly.offline.init_notebook_mode()

    data = []
    for word in document:
        if word.startswith('fragment'):
            mass = float(word.split('_')[1])
            intensity = document[word]
            data.append(
                Scatter(
                    x = [mass,mass],
                    y = [0,intensity],
                    mode = 'lines',
                    showlegend = False,
                    line = dict(
                        color = 'rgb(0.6,0.6,0.6)',
                        ),
                    )
                )
    plotly.offline.iplot({'data':data})
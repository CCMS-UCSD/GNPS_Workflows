# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 18:53:38 2017

@author: ilaponog
"""

#Importing standard and external modules
import os
import h5py
import numpy as np
import traceback
import sys;
import time;
from scipy import sparse 

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path);

#Import local/internal modules
import proc.io.manageh5db as mh5
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA

from proc.procconfig import PeakDetection_options

from proc.utils.cmdline import OptionsHolder
from proc.utils.signalproc import get_threshold;
from proc.utils.timing import tic, toc;
from proc.utils.msmanager import H5BaseMSIWorkflow as h5Base
from proc.utils.h5utils import h5write_strings;
from proc.utils.printlog import printlog, start_log, stop_log;

filename= 'i:/FTP/GCMS/MSV000080892/Results6/GC_data_for_Jamie.h5';

ncomp = 20
X_3D  = mh5.load_dataset(filename, '/spproc2D_peakdetect' + '/X_3D')
X2D   = X_3D[:,:,24]
nmf_1 = NMF(n_components = ncomp, init='nndsvd')

W = nmf_1.fit_transform(X2D)  # integral spectra
H = nmf_1.components_ # quantity integrals (fragmentation patterns/spectra)

denom = np.sum(np.power(X2D,2))
nmf_comp_variance = np.zeros(ncomp)

for i in range(ncomp):
    nmf_comp_variance[i] = 1-np.sum(np.power(X2D - np.dot(np.matrix(W[:,i]).transpose(),np.matrix(H[i,:])),2))/denom    
    
    
    
pca_model = PCA(n_components = ncomp)

W = pca_model.fit_transform(X2D)
H = pca_model.components_

denom = np.sum(np.power(X2D - np.mean(X2D,axis=0),2))
pca_comp_variance = np.zeros(ncomp)

for i in range(ncomp):
    pca_comp_variance[i] = 1 - np.sum(np.power(X2D - pca_model.mean_ - np.dot(np.matrix(W[:,i]).transpose(),np.matrix(H[i,:])),2))/denom        
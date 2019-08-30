# -*- coding: utf-8 -*-
"""
***********************************************************************
BASIS: Processing of large-scale mass spectrometry imaging datasets
***********************************************************************
 
The package includes a set of modules for optimized analytical 
pre-processing workflow for raw MSI data. It accounts for common 
bio-analytical complexities (including data volume burden, 
platform specific bias and heteroscedastic noise structure) 
inherent to high-throughput MALDI- and DESI-MSI datasets of 
tissue specimens. 

This workflow is an essential prerequisite 
for processing and integrating heterogeneous 
MSI datasets for downstream machine learning approaches.

The modules include:  

    *  HDF5-based Database: to organise, retrieve and store large volumes of numerical MS imaging datasets
    *  Peak alignment: to adjust for any differences of mz or ccs instrumental measurements of molecular ion species across  datasets                    
    *  Inter-sample normalization: to account for overall intensity differences between MSI datasets of multiple tissue samples.  
    *  Intra-sample normalization: to account for overall intensity (pixel to pixel) variation between spectra within individual datasets
    *  Variance stabilizing transformation: to account for heteroscedastic noise structure characterized by increasing variance as a function of increased signal intensity 
    *  Cluster-driven removal of solvent/matrix related peaks

""" 

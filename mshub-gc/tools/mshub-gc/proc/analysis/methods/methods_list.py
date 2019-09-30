# -*- coding: utf-8 -*-
"""
Created on Wed Oct 04 14:35:42 2017

Holder for available analysis methods

New statistical methods should be registered here. 
Main statistical method class should be added to the dictionary
available_stat_analysis_methods with its name as a key. 
Settings and command line options specific to the method 
should be added to procconfig_options_for_methods. 
See ANOVA implementation for example. 


Dr. Ivan Laponogov
"""


available_stat_analysis_methods = {};  #Registry of available methods.
procconfig_options_for_methods = [];  #List of command line options for the methods registered.

#ANOVA method registration
from proc.analysis.methods.anova import ANOVA_Statistical_Analysis, ANOVA_procconfig_settings;
available_stat_analysis_methods['ANOVA'] = ANOVA_Statistical_Analysis;
procconfig_options_for_methods.append(ANOVA_procconfig_settings);
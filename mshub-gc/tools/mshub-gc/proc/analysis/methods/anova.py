# -*- coding: utf-8 -*-
"""
Created on Wed Oct 04 14:56:58 2017

Implementation of ANOVA statistical analysis
Can be used as template for other methods.
Uses statsmodels for ANOVA analysis 
and pandas for data representation.


Author: Dr. Ivan Laponogov
"""

#Importing standard and external modules
import os; 
import sys;
import traceback #This is for displaying traceback in try: except: constructs
import time;

import h5py
import numpy as np
import traceback;
from pandas import DataFrame, isnull;
import statsmodels.api as sm
from statsmodels.formula.api import ols


#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        #Use print here instead of printlog as printlog is not yet imported! 
        #The rest should have printlog in place of print.
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path); 
    

#Import local/internal modules

#Timing functions for standard stats output
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog;

import proc.io.manageh5db as mh5

from proc.utils.cmdline import Option, Value, AllValues, PathExists, GreaterOrEqual;





class ANOVA_Statistical_Analysis(object):
    '''
    Statistical analysis class definition (ANOVA). Must expose analyse method 
    with no parameters other than self. 
    Should define parameters dictionary to describe calculable parameters grouped by
    parameter groups. Names of groups can contain HTML tags for formatting
    Group name is used as a key in this dictionary, value is a list of lists,
    where every sublist contains three strings corresponding to:
    1) internal, pythonic name of the parameter returned by the statistical method 
    (also used in group_by list);
    2) name of the parameter for report in HTML, can contain HTML tags for formatting;
    3) name of the parameter as it is returned by the statistical method implemented. It is used
    for name conversion from the statistical library used to the one used internally
    by these modules. See below for example.
    
    Also additional_groups list has to be defined to list returned values in addition
    to those defined in your statistical model, e.g. Residual for ANOVA.
    
    __init__ should take stat_model instance and methodparams dictionary as 
    input parameters.    
    
    '''

    parameters = {
        'ANOVA type 2 <br>(focus on individual factors)':
            [
                ['F',          'F',             'F'],
                ['p_value',    'p-value',       'PR(>F)'],
                #['sum_sq',     'sum sq',        'sum_sq'],
                #['df',         'df',            'df'],
            ],

        'Diagnostics':
            [       
                ['p_value_threshold',  'p-value threshold pass',    'p_value_pass'],
            ],
        
        };
        
        
    
    additional_groups = [
        'Residual',
        ];

    def __init__(self, stat_model, methodparams):
        """
        ANOVA method initialization.
        Args: stat_model - instance of the StatisticalModel class;
              methodparams - dictionary of supplied method parameters;
              
        
        """
        self.stat_model = stat_model;
        self.methodparams = methodparams;
        
        
        printlog('\nInitialized ANOVA analyser...');
        self.p_value_threshold = self.methodparams['p_value'];
        printlog('\np-value threshold: %.5f'%self.p_value_threshold);
        
        #if self.methodparams['interactions_expected'] == 'no':
        #    self.anova_type = 2;
        #    printlog('Interactions not expected. Using ANOVA type 2...')
        #else:
        #    self.anova_type = 3;
        #    printlog('Interactions expected. Using ANOVA type 3...')
            
        if self.methodparams['robust'] == 'None':
            self.robust = None;
            printlog('Robust covariance not used...')
        else:
            self.robust = self.methodparams['robust'];
            printlog('Using covariance %s...'%self.robust);
    
            
    def analyse(self):
        """
        Performs analysis using ANOVA on the StatisticalModel instance supplied at the initialization step
        
        """
        printlog('\nAnalysing...')
        
        #Initialize output for stat_model. Parameters and additional_groups need to be passed as arguments to prepare
        #stat_model instance to receive the results of analysis.
        self.stat_model.initialize_output(
        parameters =  self.parameters,
        additional_groups = self.additional_groups
        );
        
        #Iterate over the available data in stat_model. Each iteration deals with on of the selected rt peaks. 
        #Each iteration returns data as a dictionary containing experimental values of 
        #quantity integrals for the corresponding peak and the metadata values for selected metadata categories.
        #E.g. data = {'quantity_integrals':[1.1,2.2,1.3,4.8], 'dose':[1,2,1,2], 'time':[8,12,24,48]} for 
        #model 'C(dose)*C(time)'
        #During iteration self.stat_model.current_index contains the index of the item of self.stat_model.rt_indeces array being processed.
        #self.stat_model.current_rt contains current rt value in seconds
        #self.stat_model.model_clean contains a clean string representation of your model, e.g.
        #for input model 'C(dose)*C(time)' you will have 'C(dose)+C(time)+C(dose):C(time)'
        
        for data in self.stat_model.data():
            printlog('\n%s of %s: %.3f min.'%(self.stat_model.current_index + 1, len(self.stat_model.rt_indeces), self.stat_model.current_rt / 60.0));
            
            #for ANOVA from statsmodels add quantity_integrals to the string model representation            
            model_description = 'quantity_integrals ~ ' + '+'.join(self.stat_model.model_clean);
            #prepare dataframe 
            dataframe = DataFrame(data = data);
            
            #fit linear model
            lm = ols(model_description, data = dataframe).fit();
            printlog(lm.summary());
            printlog('\n');
            
            try: #Sometimes ANOVA can fail, thus try:except 
                    
                #Do ANOVA            
                anova = sm.stats.anova_lm(lm, typ = 2, robust = self.robust);
                
                #results are converted from transposed dataframe to dictionary                
                #This way your results will contain a dictionary of dictionaries
                #with groups and group combinations from the model as the key
                #for the first level dictionary and calculated parameters 
                #as keys for the inner dictionaries, e.g.
                # results = {
                #  'C(Virus):C(Time)':  {'PR(>F)': 0.66408762493566431, 'sum_sq': 56504705293.388962, 'F': 0.60495953227434596}, 
                #  'C(Time)'         :  {'PR(>F)': 0.20201607440256636, 'sum_sq': 81742622757.011337, 'F': 1.7503313599529786}, 
                #  'C(Virus)'        :  {'PR(>F)': 0.80706629815712594, 'sum_sq': 10130541575.940208, 'F': 0.21692238413226958}, 
                #  'Residual'        :  {'PR(>F)': nan,                 'sum_sq': 420311046036.94336, 'F': nan}
                #  }
                results = anova.transpose().to_dict();
                
                
                #For results calculate background color to be used in HTML report based on the values obtained
                results_color = {};
                for key in results: #for each returned group
                    result_set = results[key]; #get subgroup
                    
                    p_value = result_set['PR(>F)']; #get p-value
                    if isnull(p_value):  #if not calculable - set color to grey
                        color = 0x505050;
                    elif p_value <= self.p_value_threshold: #if less than p_value_threshold - the result color is green
                        color = 0x90FF90;
                    else:
                        color = 0xFF9090;#if p_value_threshold is not passed - the result color is red
                    
                    #apply coloring to all results 
                    result_set_color = {}    #initialize dictionary for coloring of the result_set
                    results_color[key] = result_set_color; #add it to overall results_color
                    for subkey in result_set:
                        if isnull(result_set[subkey]): #if the result value for this group/subgroup is not calculable - the color is grey
                            result_set_color[subkey] = 0x505050;
                        else:
                            result_set_color[subkey] = color; #otherwise the color is based on the p_value_threshold being satisfied.
                    if not (isnull(p_value)) and p_value <= self.p_value_threshold: #Also add p_value_pass as one of the returned result values
                        result_set['p_value_pass']  = 1.0; #set it to 1 if the p_value_threshold is satisfied
                        result_set_color['p_value_pass'] = 0x90FF90;# color is green
                    else:
                        result_set['p_value_pass']  = 0.0; #0 otherwise
                        result_set_color['p_value_pass'] = 0xFF9090;# color is red
                        
                            
                #send results and their colors to stat_model for storage and reporting.                
                #stat_model instance will parse and display them according to the parameters and additional groups provided in 
                #self.stat_model.initialize_output(parameters, additional_groups)            
                self.stat_model.store_results(results, results_color);  
            except Exception as inst:
                
                printlog('ANOVA failed!');
                printlog(inst);
                traceback.print_exc();

            #TODO: Do add some diagnostics
            
            
#create list for possible grouping values
_possible_grouping_values = [];        

#fill the possible grouping values list with the values from parameters of the statistical method:
for key in ANOVA_Statistical_Analysis.parameters:
    parameter_list = ANOVA_Statistical_Analysis.parameters[key];
    for parameter in parameter_list:
        _possible_grouping_values.append(parameter[0]);
        

#Define method name value and corresponding method-related default parameters for inclusion into 
#procconfig Stat_analysis_options. For modular architecture, please do not put them directly
#into procconfig.

ANOVA_procconfig_settings = Value('ANOVA', help = 'ANOVA analysis', parameters = [
                               Option('--p_value', help = 'p-value threshold.', values=[0.05, None], type=float, targets=['/methodparams'], level = 0), 
                               Option('--group_by', help = 'Group results by.', values = _possible_grouping_values, type=str, is_list = True, targets=['/grouping'], level = 0), 
                               Option('--group_weights', help = 'Weights for groups.', values = [1.0, None], type=float, is_list = True, targets=['/grouping'], level = 0), 
                               Option('--n_groups', help = 'Number of expected groups for clustering results', values = [8, None], type=int, targets=['/grouping'], level = 0),  
                               #Option('--group_distance_function', help = 'Used distance function during grouping.', values=['euclidean', 'multiplication'], type=str, targets=['/grouping'], level = 0), 
                               #Option('--interactions_expected', help = 'Use type III Anova if interactions expected, type II is used otherwise.', values=['no', 'yes'], type=str, targets=['/methodparams'], level = 0), 
                               Option('--robust', help = 'Use heteroscedasticity-corrected coefficient covariance matrix. If robust covariance is desired, use hc3.', values=['hc3', 'hc0', 'hc1', 'hc2', 'None'], type=str, targets=['/methodparams'], level = 0), 
                               ])


    
    
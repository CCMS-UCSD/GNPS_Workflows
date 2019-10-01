#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018

@author: Zheng Zhang and Louis Felix Nothias, UC San Diego
@purpose: to convert the MetaboScape output into a diserable format. Support for PASEF.
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):

    # Transform the header to be final result format
    # SHARED_NAME -> row ID
    # RT - > row retention time
    # PEPMASS -> row m/z
    # filename - > filename + Peak area
    input_format = pd.read_csv(input_filename,index_col=None)

    # Check if PASEF data files and process accordingly
    if 'MaxIntensity' in input_format.columns:
        intensities = input_format.loc[:, 'MaxIntensity':]
        intensities = intensities.drop(['MaxIntensity'],axis = 1)
        metadata = input_format.loc[:,:'MaxIntensity']
        metadata_filtered = metadata[['FEATURE_ID','PEPMASS','RT']]
        results = pd.concat([metadata_filtered,intensities], axis=1)
        results.rename(columns={'FEATURE_ID': 'row ID','PEPMASS': 'row m/z','RT':'row retention time'}, inplace=True)

        for i in range(3,len(results.columns.values)):
            results.columns.values[i] += ".d Peak area"

        cols = list(results)
        cols[1], cols[2] = cols[2], cols[1]
        results = results.reindex (columns=cols)
        results.to_csv(output_filename,index = False)

    # If not PASEF, assuming MetaboScape files are originating from a LC-MS/MS experiment, and process accordingly
    else:
        output_format = input_format.drop(['SHARED_NAME','NAME','MOLECULAR_FORMULA','ADDUCT','KEGG', 'CAS'],axis = 1)
        output_format.columns.values[0]="row ID"
        output_format.columns.values[1]="row retention time"
        output_format.columns.values[2] = "row m/z"

        for i in range(3,len(output_format.columns.values)):
            output_format.columns.values[i] += " Peak area"

        cols = list(output_format)
        cols[1], cols[2] = cols[2], cols[1]
        results = output_format.reindex (columns=cols)
        results.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be only one input file
    main(sys.argv[1], sys.argv[2])

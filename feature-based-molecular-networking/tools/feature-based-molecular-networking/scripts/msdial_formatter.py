#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018, and updated April 2 2019

@author: zheng zhang, louis felix nothias, mingxun wang & Chris Pook
@purpose: to convert the MS-DIAL file into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    
    # first enumerate samples in the input
    n_df = pd.read_csv(input_filename, sep='\t', skiprows=3, nrows = 5)
    sample_columns = list(n_df)
    last_sample_column = sample_columns.index('Average')
    
    # now process the rest of the data
    input_df = pd.read_csv(input_filename, sep='\t', skiprows=4)
        
    #Check IMS data columns and drop them
    if 'Average drift time' in input_df.columns:
        input_df = input_df.drop(['Average drift time','Average CCS'], axis=1)

    #Continue with the processing
    headers = list(input_df.keys())
    sample_names = headers[32:last_sample_column]

    columns = ["Alignment ID", "Average Mz", "Average Rt(min)"] + sample_names
    output_df = input_df[columns].copy()

    output_columns = ["row ID", "row m/z", "row retention time"]
    output_columns += [sample_name + " Peak area" for sample_name in sample_names]
    column_name_dict = dict(zip(columns, output_columns))
    output_df.rename(columns = column_name_dict, inplace=True)
    output_df.to_csv(output_filename, sep=",", index=False)
    return

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

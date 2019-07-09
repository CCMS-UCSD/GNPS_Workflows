#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 14:47:58 2018. Modified on April 1 2019.

@author: zheng zhang and louis felix nothias
@purpose: to convert the xsms output into a diserable format
"""

import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename,index_col=None,sep='\t')
    #Prepare left table with ID mz rt
    input_format.columns.values[0]="row ID"
    input_format.columns.values[1]="row m/z"
    input_format.columns.values[4]= "row retention time"
    table_part_left = input_format[['row ID', 'row m/z','row retention time']]

    #Prepare right table with ms filename
    list_data_filename = list(input_format.filter(regex='.mzML|.mzXML|.mzml|.mzxml|.raw|.cdf|.CDF|.mzData|.netCDF|.netcdf|.mzdata'))
    table_part_right = input_format[list_data_filename]

    ## Add Peak area
    for i in range(0,len(table_part_right.columns.values)):
        table_part_right.columns.values[i] += " Peak area"
    ## Do some table processing
    table_part_right.fillna(value=0, inplace=True)
    table_part_left['row ID'] = table_part_left['row ID'].str.slice(start=2)
    table_part_left[['row ID']] = table_part_left[['row ID']].apply(pd.to_numeric)
    ## Join back the tables
    output_format = pd.concat([table_part_left, table_part_right], axis=1, join='inner')
    output_format.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1],sys.argv[2])

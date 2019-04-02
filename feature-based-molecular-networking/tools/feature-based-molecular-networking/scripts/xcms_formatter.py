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
    # Transform the header to be final result format
    # mzmed - > row m/z
    # rtmed -> row retention time
    # filename - > filename + Peak area
    input_format = pd.read_csv(input_filename,index_col=None,sep='\t')
    output_format = input_format.drop(['mzmin','mzmax','rtmin',
                                        'rtmax', 'npeaks','sample'],axis = 1)
    output_format.columns.values[0]="row ID"
    output_format.columns.values[1]="row m/z"
    output_format.columns.values[2] = "row retention time"
    for i in range(3,len(output_format.columns.values)):
        output_format.columns.values[i] += " Peak area"
    output_format.fillna(value=0, inplace=True)
    output_format['row ID'] = output_format['row ID'].str.slice(start=2)
    output_format[['row ID']] = output_format[['row ID']].apply(pd.to_numeric)
    output_format.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 14:47:58 2018

@author: zheng zhang
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
    output_format = input_format.drop(['Row.names','mzmin','mzmax','rtmin',
                                       'rtmax', 'npeaks','sample'],axis = 1)
    output_format.columns.values[0]="row m/z"
    output_format.columns.values[1] = "row retention time"
    for i in range(2,len(output_format.columns.values)):
        output_format.columns.values[i] += " Peak area"
    cols = list(output_format)
    output_format = output_format.reindex (columns=cols)
    output_format.insert(0, 'row ID', output_format.index+1)
    output_format.fillna(value=0, inplace=True)
    output_format.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1])

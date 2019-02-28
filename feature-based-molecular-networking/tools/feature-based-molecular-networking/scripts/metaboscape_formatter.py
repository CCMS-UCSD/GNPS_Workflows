#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018

@author: zheng zhang
@purpose: to convert the metaboScape output into a diserable format
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
    output_format = input_format.drop(['NAME','MOLECULAR_FORMULA','ADDUCT','SHARED_NAME', 'KEGG', 'CAS'],axis = 1)
    output_format.columns.values[0]="row ID"
    output_format.columns.values[1]="row retention time"
    output_format.columns.values[2] = "row m/z"
    for i in range(3,len(output_format.columns.values)):
        output_format.columns.values[i] += " Peak area"
    cols = list(output_format)
    cols[1], cols[2] = cols[2], cols[1]
    output_format = output_format.reindex (columns=cols)
    output_format.to_csv(output_filename,index = False)



if __name__=="__main__":
    # there should be obly one input file
    main(sys.argv[1], sys.argv[2])

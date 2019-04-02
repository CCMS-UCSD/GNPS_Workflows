#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018, and updated April 2 2019

@author: zheng zhang and louis felix nothias
@purpose: to convert the MS-DIAL file into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename, index_col=None, sep ='\t')
    input_format = input_format[2:]
    columns_to_drop = [-1]+list(range(3,21))
    output_format = input_format.drop(input_format.columns[columns_to_drop],axis = 1)
    header = output_format.iloc[0]
    output_format = output_format.rename(columns = header)
    output_format = output_format[1:]
    output_format.columns.values[0]="row ID"
    output_format.columns.values[2] = "row m/z"
    output_format.columns.values[1] = "row retention time"
    output_format = output_format.drop(columns=['MS/MS spectrum'])
    for i in range(3,len(output_format.columns.values)):
        output_format.columns.values[i] += " Peak area"

    output_format.to_csv(output_filename,sep=',',index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_to_csv(sys.argv[1], sys.argv[2])

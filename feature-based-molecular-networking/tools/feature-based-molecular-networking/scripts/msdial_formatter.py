#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018

@author: zheng zhang
@purpose: to convert the MS-DIAL file into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # Transform the header to be final result format
    # Index -> row ID
    # Average Mz-> row m/z
    # Average Rt(min)- > row retention time
    # filename - > filename + Peak area
    input_format = pd.read_csv(input_filename,index_col=None,sep ='\t')
    input_format = input_format[2:]
    columns_to_drop = [0]+list(range(3,21))
    output_format = input_format.drop(input_format.columns[columns_to_drop],axis = 1)
    #output_format.set_index(output_format.iloc[1].values)
    header = output_format.iloc[0]
    output_format = output_format.reset_index(drop=True)
    output_format = output_format[1:]
    output_format = output_format.rename(columns = header)

    columns_to_drop = [0]+list(range(3,21))
    #output_format = input_format.drop(input_format.columns[columns_to_drop],axis = 1)
    output_format.columns.values[0]="row retention time"
    output_format.columns.values[1] = "row m/z"
    for i in range(2,len(output_format.columns.values)):
        output_format.columns.values[i] += " Peak area"
    output_format = output_format.reset_index(drop=False)
    output_format.columns.values[0] = "row ID"
    
    output_format.to_csv(output_filename,sep=',',index = False)


if __name__=="__main__":
    # there should be obly one input file
    convert_to_csv(sys.argv[1], sys.argv[2])

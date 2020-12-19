#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 12:23:48 2018

@author: zheng zhang
@purpose: to convert the openms output into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename,index_col=None,header=None).T
    input_format.columns = input_format.iloc[0]

    # row m/z is the first element
    # row retention time is the second element
    mz_rt = pd.DataFrame(input_format['Sample name'].str.split(' ',2).tolist(),
                                   columns = ['row m/z','row retention time','to_drop'])
    output_format = pd.concat([mz_rt, input_format], axis=1)
    output_format = output_format.reindex(output_format.index.drop(0))

    # filename - > filename + Peak area
    header = output_format.columns.values.tolist()
    for i in range(header.index('FMEDIAN Fractions')+1,len(header)):
        header[i] += " Peak area"
    output_format.columns = header

    # find the columns that wont be included in the output
    drop_columns_idx= list(range(header.index('to_drop'),header.index('FMEDIAN Fractions')+1))
    output_format = output_format.drop(output_format.columns[drop_columns_idx],axis=1)


    # write csv
    output_format.insert(0, 'row ID', output_format.index)
    output_format.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_from_optimus(sys.argv[1], sys.argv[2])

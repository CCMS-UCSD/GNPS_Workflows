#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 12:23:48 2018 and updated on Dec 2020
@author: zheng zhang and Louis Felix Nothias @UC San Diego
@purpose: to convert the Optimus OpenMS output into a diserable format
"""
import pandas as pd
import sys

def convert_from_optimus(input_filename, output_filename):
    input_format = pd.read_csv(input_filename,index_col=None,header=None).T
    input_format.columns = input_format.iloc[0]

    # row m/z is the first element
    # row retention time is the second element
    mz_rt = pd.DataFrame(input_format['Sample name'].str.split(' ',2).tolist(),
                                    columns = ['row m/z','row retention time','to_drop'])
    output_format = pd.concat([mz_rt, input_format], axis=1)
    output_format = output_format.reindex(output_format.index.drop(0))

    # We are dropping columns that are not needed
    column_string = ['FTIC', 'FMEAN','FMEDIAN','to_drop','Sample name']
    for string in column_string:
        output_format.drop([col for col in output_format.columns if string in col],axis=1,inplace=True)

    # filename - > filename + Peak area
    header = output_format.columns.values.tolist()
    for i in range(2,len(header)):
        header[i] += " Peak area"
    output_format.columns = header

    # write csv
    output_format.insert(0, 'row ID', output_format.index)
    output_format.to_csv(output_filename,index = False)

if __name__=="__main__":
    # Provide input and output path/filenames
    convert_from_optimus(sys.argv[1], sys.argv[2])

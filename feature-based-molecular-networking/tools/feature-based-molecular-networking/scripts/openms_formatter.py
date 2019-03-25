#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 17:31:35 2018

@author: zheng zhang
@purpose: to convert the openms output into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # read file line by line, find
    # 1, all the spectrum files
    # 2, start of consensus
    # 3, header of consensus (start with #consensus)
    spectrum_files=[]
    start_row_consensus = 0
    header_consensus = -1

    f = open(input_filename)
    for line in f:
        if line.startswith('CONSENSUS') :
            break
        if line.startswith('MAP'):
            filename = line.split('\t')[2].split('/')[-1]
            spectrum_files.append(filename)
        elif line.startswith('#CONSENSUS'):
            header_consensus = line.strip('\n').split('\t')
        start_row_consensus += 1
    f.close()

    #check duplicates
    if len(spectrum_files) != len(set(spectrum_files)):
        print ('The feature table contains duplicated filename(s). Update the filename(s) in the feature table and the metadata table')
        return

    # Transform the header to be final result format
    # rt_cf -> row retention time
    # mz_cf- > row m/z
    # intensity_0 -> septrum_files[0]. Peak area ...
    innerLoop_iterator = 0
    for i in range(len(header_consensus)):
        if header_consensus[i] == 'rt_cf':
            header_consensus[i] = 'row retention time'
        elif header_consensus[i] == 'mz_cf':
            header_consensus[i] = 'row m/z'
        # modify the intensity columns to be file peak area
        while header_consensus[i].startswith('intensity') and not header_consensus[i].startswith('intensity_cf') and innerLoop_iterator < len(spectrum_files):
            spectrum_files[innerLoop_iterator] = spectrum_files[innerLoop_iterator]+' Peak area'
            header_consensus[i] = spectrum_files[innerLoop_iterator]
            i += 1
            innerLoop_iterator += 1


    result = pd.read_csv(input_filename,sep='\t',index_col=None,
                         skiprows=range(0,start_row_consensus),
                         names = header_consensus)
    result.fillna(value=0, inplace=True)
    result.insert(0, 'row ID', result.index+1)
    to_write_list = ['row ID','row m/z','row retention time']+spectrum_files
    result.to_csv(output_filename,index = False,
                  columns = to_write_list)

if __name__=="__main__":
    # there should be obly one input file
   convert_to_feature_csv(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # Transform the header to be 
    input_quantification = pd.read_csv(input_filename,sep=',')

    filename = list(input_quantification.columns)
    append_str = ' Peak area'
    rename_filename = [sub + append_str for sub in filename[3:]]
    rename = filename[:3] + rename_filename
    input_quantification.columns = rename
    input_quantification.to_csv(output_filename,index = False)

###function verifies that the quant table follows proper mzmine format
def validate_mzmine_output_file(quant_table_filename):
    required_columns = ["row ID", "row retention time", "row m/z"]
    file_open = open(quant_table_filename, 'r')
    first_line = next(file_open)

    #try splitting it by comma
    all_columns_list = first_line.split(",")
    
    #make sure the manatory headings are in the file
    assert(set(required_columns).issubset(set(all_columns_list)))

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2]) 

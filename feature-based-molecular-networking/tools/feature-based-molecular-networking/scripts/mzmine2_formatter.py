#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # Transform the header to be final result format
    input_quantification = pd.read_csv(input_filename,sep=',')

    valid_extensions = [
        ".raw ",
        ".RAW ",
        ".mzML ",
        ".mzXML ",
        ".CDF ",
        ".d ",
        ".mgf ",
        ".MGF ",
        ".mzData ",
        ".lcd ",
        ".wiff ",
        ".scan "
    ]
    
    rename_mapping = {}
    for key in input_quantification.keys():
        if "Peak area" in key:
            #Removing everything after an expected extension
            for valid_extension in valid_extensions:
                if valid_extension in key:
                    end_index = key.rfind(valid_extension) + len(valid_extension) - 1
                    filename = key[:end_index]
                    print("Renaming", key, "to", filename + " Peak area")
                    rename_mapping[key] = filename + " Peak area"
                    continue
    
    input_quantification.rename(columns=rename_mapping, inplace=True)
    input_quantification.to_csv(output_filename,index = False)

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 17:20:37 2018, and updated April 2 2019

@author: zheng zhang, louis felix nothias, and mingxun wang
@purpose: to convert the MS-DIAL file into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename, sep='\t', skiprows=3)

    #Check IMS data columns and drop them
    if 'Average drift time' in input_format.columns:
        input_format = input_format.drop(['Average drift time','Average CCS'], axis=1)

    #Continue with the processing
    headers = list(input_format.keys())
    sample_names = headers[22:]

    input_records = input_format.to_dict(orient="records")
    output_records = []

    for record in input_records:
        scan = record["Alignment ID"]
        mz = record["Average Mz"]
        rt = record["Average Rt(min)"]

        output_record = {}
        output_record["row ID"] = str(scan)
        output_record["row m/z"] = str(mz)
        output_record["row retention time"] = str(rt)

        for sample_name in sample_names:
            output_record[sample_name + " Peak area"] = record[sample_name]

        output_records.append(output_record)

    output_headers = ["row ID", "row m/z", "row retention time"]
    output_headers += [sample_name + " Peak area" for sample_name in sample_names]

    output_df = pd.DataFrame(output_records)
    output_df.to_csv(output_filename, sep=",", index=False, columns=output_headers)

    return

if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

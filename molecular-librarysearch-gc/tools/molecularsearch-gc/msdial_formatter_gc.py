#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 2020 by Louis Felix

@author: zheng zhang, louis felix nothias, and mingxun wang
@purpose: to convert the MS-DIAL file into a diserable format for GC-MS
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename, sep='\t', skiprows=4)

    # Crop out the two last columns (Average and Stdev)
    input_format = input_format[input_format.columns[:-2]]

    #Continue with the processing
    headers = list(input_format.keys())
    sample_names = headers[28:]

    input_records = input_format.to_dict(orient="records")
    output_records = []

    for record in input_records:
        scan = record["Alignment ID"]
        mz = record["Quant mass"]
        rt = record["Average Rt(min)"]

        output_record = {}
        output_record["row ID"] = str(int(scan)+1)
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

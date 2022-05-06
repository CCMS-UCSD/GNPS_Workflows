#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: mingxun wang
@purpose: to convert the Agilent file into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    input_df = pd.read_csv(input_filename, sep=',')

    # Getting the sample names
    not_sample_names = ["Compound Name", "Formula", "Mass", "RT", "CAS ID"]
    sample_names = list(input_df.columns)
    sample_names = set(sample_names) - set(not_sample_names)
    sample_names = list(sample_names)

    output_df = pd.DataFrame()
    output_df["row ID"] = range(1, len(input_df) + 1)
    output_df["row m/z"] = input_df["Mass"]
    output_df["row retention time"] = input_df["RT"]

    for sample_name in sample_names:
        output_df[sample_name + " Peak area"] = input_df[sample_name]

    # Writing the output headers
    output_headers = ["row ID", "row m/z", "row retention time"]
    output_headers += [sample_name + " Peak area" for sample_name in sample_names]

    output_df.to_csv(output_filename, sep=",", index=False, columns=output_headers)

    return

# Adding scan numbers in the MGF
def convert_mgf(input_mgf, output_mgf):
    output_file = open(output_mgf, "w")
    scan = 1

    for line in open(input_mgf):
        if "BEGIN IONS" in line:
            output_file.write(line)
            output_file.write(
                """SCANS={}
FEATURE_ID={}
MSLEVEL=2\n""".format(scan, scan)
            )
            scan += 1
        else:
            output_file.write(line)

    return


if __name__=="__main__":
    # there should be obly one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

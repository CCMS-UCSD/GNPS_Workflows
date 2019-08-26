#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the mztab output into a diserable format
"""
from io import StringIO
import pandas as pd
import sys
import os

#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_csv(input_filename, output_filename):
    MTD_lines = []
    SML_lines = []
    SMF_lines = []
    SME_lines = []

    for line in open(input_filename):
        if line.split("\t")[0] in ["SMH", "SML"]:
            SML_lines.append(line)
        if line.split("\t")[0] in ["SFH", "SMF"]:
            SMF_lines.append(line)
        if line.split("\t")[0] in ["SEH", "SME"]:
            SME_lines.append(line)
        if line.split("\t")[0] in ["MTD"]:
            MTD_lines.append(line)

    sml_data = pd.read_csv(StringIO("".join(SML_lines)), sep="\t")
    smf_data = pd.read_csv(StringIO("".join(SMF_lines)), sep="\t")
    sme_data = pd.read_csv(StringIO("".join(SME_lines)), sep="\t")

    #Parsing out metadata
    mtd_data = pd.read_csv(StringIO("".join(MTD_lines)), sep="\t", header=None)[[0, 1, 2]]
    mtd_data.columns = ['MTD', 'type', 'value']

    ms_run_to_filename = {}
    for record in mtd_data.to_dict(orient="records"):
        if "ms_run" in record["type"] and "location" in record["type"]:
            ms_run_to_filename[record["type"].split("-")[0]] = os.path.basename(record["value"])
    print(ms_run_to_filename)

    assay_to_msrun = {}
    for record in mtd_data.to_dict(orient="records"):
        if "assay" in record["type"] and "ms_run_ref" in record["type"]:
            assay_to_msrun[record["type"].split("-")[0]] = record["value"]
    print(assay_to_msrun)


    for record in smf_data.to_dict(orient="records"):
        for assay in assay_to_msrun:
            

    

    return {}

#TODO: Finish this function to read the input files and find the MS2 and actually extract the peaks into an MGF
def create_mgf(input_filenames, output_mgf, compound_filename_mapping, name_mangle_mapping=None):
    return None

if __name__=="__main__":
    # there should be obly one input file
   compound_filename_mapping = convert_to_feature_csv(sys.argv[1], sys.argv[2])

   import glob
   create_mgf(os.path.join(sys.argv[3], "*"), sys.argv[4], compound_filename_mapping)

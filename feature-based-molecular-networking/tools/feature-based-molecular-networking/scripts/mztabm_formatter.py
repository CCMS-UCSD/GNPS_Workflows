#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the mztab output into a diserable format
"""
from io import StringIO
import pandas as pd
import sys

#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_csv(input_filename, output_filename):
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

    sml_data = pd.read_csv(StringIO("".join(SML_lines)), sep="\t")
    smf_data = pd.read_csv(StringIO("".join(SMF_lines)), sep="\t")
    sme_data = pd.read_csv(StringIO("".join(SME_lines)), sep="\t")

    

    return

if __name__=="__main__":
    # there should be obly one input file
   convert_to_feature_csv(sys.argv[1], sys.argv[2])

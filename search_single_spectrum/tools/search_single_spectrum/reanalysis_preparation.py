#!/usr/bin/python

import sys
import getopt
import os
import json
import requests
import pandas as pd

def main():
    input_files_filename = sys.argv[1]
    output_filename = sys.argv[2]

    try:
        filenames_df = pd.read_csv(input_files_filename, sep="\t")
        all_filenames = list(filenames_df["filename"])

        params_dict = {}
        params_dict["desc"] = "Meta-Analysis on GNPS"
        params_dict["workflow"] = "METABOLOMICS-SNETS-V2"
        params_dict["library_on_server"] = "d.speclibs;"
        params_dict["spec_on_server"] = ";".join(all_filenames)

        output_file = open(output_filename, "w")
        output_file.write("filenames\n")
        output_file.write(";".join(all_filenames))
    except:
        output_file = open(output_filename, "w")
        output_file.close()

if __name__ == "__main__":
    main()

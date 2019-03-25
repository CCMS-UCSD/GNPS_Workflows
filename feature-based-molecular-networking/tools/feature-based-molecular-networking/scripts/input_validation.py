#!/usr/bin/python

import pandas as pd
import os
import argparse
import statistics
import glob
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Validation of Input Parameters')
    parser.add_argument('params_xml', help='params_xml')
    parser.add_argument('quantification_table', help='quantification_table')
    parser.add_argument('input_mgf', help='input_mgf')
    parser.add_argument('metadata_table', help='metadata_table')
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_table, "*"))
    if len(metadata_files) == 1:
        metadata_df = pd.read_csv(metadata_files[0], sep="\t")
        if not "filename" in metadata_df:
            print("filename header not in metadata file, please refer to documentation - https://ccms-ucsd.github.io/GNPSDocumentation/networking/#metadata ")
            exit(1)



    exit(0)


if __name__ == "__main__":
    main()

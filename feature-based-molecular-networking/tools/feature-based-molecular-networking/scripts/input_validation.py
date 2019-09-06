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
    parser.add_argument('input_spectra', help='input_spectra')
    parser.add_argument('metadata_table', help='metadata_table')
    args = parser.parse_args()

    #Checking if metadata file includes the right information
    metadata_files = glob.glob(os.path.join(args.metadata_table, "*"))
    if len(metadata_files) == 1:
        metadata_df = pd.read_csv(metadata_files[0], sep="\t")
        print("Read length of metadata", len(metadata_df))
        metadata_df = metadata_df.dropna(how="all")
        print("Empty line filtered length of metadata", len(metadata_df))

        if not "filename" in metadata_df:
            print("filename header not in metadata file, please refer to documentation - https://ccms-ucsd.github.io/GNPSDocumentation/networking/#metadata ")
            exit(1)

        metadata_df["validator_count"] = 1
        metadata_df = metadata_df[metadata_df['filename'].map(len) > 1]

        metadata_grouped_df = metadata_df.groupby("filename").count()
        metadata_grouped_df["filename"] = metadata_grouped_df.index

        metadata_grouped = metadata_grouped_df.to_dict(orient="records")

        is_error = False
        for metadata_row in metadata_grouped:
            if metadata_row["validator_count"] > 1:
                print(metadata_row["filename"], "is repeated in metadata file")
                is_error = True
        if is_error:
            exit(1)
        
    exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import glob
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('metadata_summary', help='metadata_summary')
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_folder, "*"))
    if len(metadata_files) != 1:
        exit(0)

    metadata_df = pd.read_csv(metadata_files[0], sep="\t")

    output_list = []
    for column in metadata_df.columns:
        if "ATTRIBUTE_" in column:
            terms = list(set(metadata_df[column]))
            for term in terms:
                output_dict = {}
                output_dict["Attribute"] = column
                output_dict["Term"] = term
                output_list.append(output_dict)

    pd.DataFrame(output_list).to_csv(os.path.join(args.metadata_summary, "metadata_summary.tsv"), sep="\t", index=False)


if __name__ == "__main__":
    main()

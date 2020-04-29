#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import glob

def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('metadata_summary', help='metadata_summary')
    args = parser.parse_args()

    metadata_files = glob.glob(os.path.join(args.metadata_folder, "*"))
    if len(metadata_files) != 1:
        exit(0)

    metadata_df = pd.read_csv(metadata_files[0], sep="\t")

    for column in metadata_df.columns:
        print(column)



if __name__ == "__main__":
    main()

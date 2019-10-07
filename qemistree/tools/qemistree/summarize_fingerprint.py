#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse
import glob

def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("results_folder")
    parser.add_argument("summary_folder")

    args = parser.parse_args()

    input_csi_qza = os.path.join(args.results_folder, "fingerprints.qza")
    os.system("unzip {}", input_csi_qza)

    #Looking for summary filename
    search_filenames = glob.glob("**/summary_csi_fingerid.csv", recursive=True)
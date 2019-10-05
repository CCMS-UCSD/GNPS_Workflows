#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("input_sirius_mgf")
    parser.add_argument("input_quant_table")
    parser.add_argument("output_folder")
    parser.add_argument("qiime_bin")

    args = parser.parse_args()

    output_feature_qza = os.path.join(args.output_folder, "feature-table.qza")
    output_mgf_qza = os.path.join(args.output_folder, "sirius.mgf.qza")

    all_cmd = []
    cmd = "LC_ALL=en_US && export LC_ALL && {} tools tools import --input-path {} --output-path {} --type FeatureTable[Frequency]".format(args.qiime_bin, args.input_quant_table, output_feature_qza)
    all_cmd.append(cmd)

    cmd = "LC_ALL=en_US && export LC_ALL && {} tools import --input-path {} --output-path {} --type MassSpectrometryFeatures".format(args.qiime_bin, args.input_sirius_mgf, output_mgf_qza)
    all_cmd.append(cmd)

    for cmd in all_cmd:
        print(cmd)
        os.system(cmd)

if __name__ == "__main__":
    main()

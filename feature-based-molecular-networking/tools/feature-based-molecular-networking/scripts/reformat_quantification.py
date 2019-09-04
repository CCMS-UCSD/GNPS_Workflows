#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
import shutil
import openms_formatter
import optimus_formatter
import msdial_formatter
import metaboscape_formatter
import xcms_formatter
import mzmine2_formatter
import progenesis_formatter


def main():
    parser = argparse.ArgumentParser(description='Create parallel parameters')
    parser.add_argument('toolname', help='name of input tool')
    parser.add_argument('quantification_table', help='quantification_table')
    parser.add_argument('quantification_table_reformatted', help='quantification_table_reformatted')
    parser.add_argument('input_mgf', help='input_mgf')
    parser.add_argument('output_mgf', help='output_mgf')
    args = parser.parse_args()

    if args.toolname == "MZMINE2":
        print("MZMINE2")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        mzmine2_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "OPENMS":
        print("OPENMS")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        openms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "OPTIMUS":
        print("OPTIMUS")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        optimus_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "MSDIAL":
        print("MSDIAL")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        msdial_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "METABOSCAPE":
        print("METABOSCAPE")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        metaboscape_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "XCMS3":
        print("XCMS3")
        shutil.copyfile(args.input_mgf, args.output_mgf)
        xcms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "PROGENESIS":
        print("PROGENESIS")
        compound_scan_mapping = progenesis_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
        progenesis_formatter.convert_mgf(args.input_mgf, args.output_mgf, compound_scan_mapping)

if __name__ == "__main__":
    main()

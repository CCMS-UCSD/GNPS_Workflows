#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
import shutil
import glob
import proteosafe
import msdial_formatter

def main():
    parser = argparse.ArgumentParser(description='Create parallel parameters')
    parser.add_argument('toolname', help='name of input tool')
    parser.add_argument('quantification_table', help='quantification_table')
    parser.add_argument('quantification_table_reformatted', help='quantification_table_reformatted')
    parser.add_argument('input_spectra_folder', help='input_spectra_folder')
    parser.add_argument('output_mgf', help='output_mgf')
    parser.add_argument('workflowParameters', help='workflowParameters')
    args = parser.parse_args()

    input_filenames = glob.glob(os.path.join(args.input_spectra_folder, "*"))

    if args.toolname == "MZMINE2":
        print("MZMINE2")

        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        shutil.copyfile(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "MSHUB":
        print("MSHUB")
        
        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        shutil.copyfile(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "MSDIAL":
        print("MSDIAL")

        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        msdial_formatter.format_mgf(input_mgf, args.output_mgf)
        msdial_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    
if __name__ == "__main__":
    main()

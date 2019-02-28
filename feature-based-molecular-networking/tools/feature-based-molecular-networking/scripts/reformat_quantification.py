#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import shutil
import ming_proteosafe_library
import ming_fileio_library
import openms_formatter
import optimus_formatter
import msdial_formatter
import metaboscape_formatter
import xcms_formatter

def main():
    parser = argparse.ArgumentParser(description='Create parallel parameters')
    parser.add_argument('workflowParameters', help='workflowParameters')
    parser.add_argument('quantification_table', help='quantification_table')
    parser.add_argument('quantification_table_reformatted', help='quantification_table_reformatted')
    args = parser.parse_args()

    params_object = ming_proteosafe_library.parse_xml_file(open(args.workflowParameters))

    if params_object["QUANT_TABLE_SOURCE"][0] == "MZMINE2":
        shutil.copyfile(args.quantification_table, args.quantification_table_reformatted)
    elif params_object["QUANT_TABLE_SOURCE"][0] == "OPENMS":
        print("OPENMS")
        print(args.quantification_table)
        openms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif params_object["QUANT_TABLE_SOURCE"][0] == "OPTIMUS":
        print("OPTIMUS")
        optimus_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif params_object["QUANT_TABLE_SOURCE"][0] == "MSDIAL":
        print("MSDIAL")
        msdial_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif params_object["QUANT_TABLE_SOURCE"][0] == "METABOSCAPE":
        print("METABOSCAPE")
        metaboscape_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif params_object["QUANT_TABLE_SOURCE"][0] == "XCMS3":
        print("XCMS3")
        xcms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)




if __name__ == "__main__":
    main()

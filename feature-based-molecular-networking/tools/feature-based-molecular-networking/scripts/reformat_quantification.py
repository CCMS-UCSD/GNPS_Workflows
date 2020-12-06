#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
import shutil
import glob
import openms_formatter
import optimus_formatter
import msdial_formatter
import metaboscape_formatter
import xcms_formatter
import mzmine2_formatter
import progenesis_formatter
import mztabm_formatter
import proteosafe


def main():
    parser = argparse.ArgumentParser(description='Create parallel parameters')
    parser.add_argument('toolname', help='name of input tool')
    parser.add_argument('quantification_table', help='quantification_table')
    parser.add_argument('quantification_table_reformatted', help='quantification_table_reformatted')
    parser.add_argument('input_spectra_folder', help='input_spectra_folder')
    parser.add_argument('output_mgf', help='output_mgf')
    parser.add_argument('workflowParameters', help='workflowParameters')
    parser.add_argument('--QUANT_FILE_NORM', default="None", help='QUANT_FILE_NORM')
    
    args = parser.parse_args()

    input_filenames = glob.glob(os.path.join(args.input_spectra_folder, "*"))

    if args.toolname == "MZMINE2":
        print("MZMINE2")

        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        mzmine2_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "OPENMS":
        print("OPENMS")
        
        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        openms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "OPTIMUS":
        print("OPTIMUS")

        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        optimus_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "MSDIAL":
        print("MSDIAL")
        
        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        msdial_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "METABOSCAPE":
        print("METABOSCAPE")
        
        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        metaboscape_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "XCMS3":
        print("XCMS3")
        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]
        shutil.copyfile(input_mgf, args.output_mgf)
        xcms_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
    elif args.toolname == "PROGENESIS":
        print("PROGENESIS")

        if len(input_filenames) != 1:
            print("Must input exactly 1 spectrum mgf file")
            exit(1)

        input_mgf = input_filenames[0]

        compound_scan_mapping = progenesis_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
        progenesis_formatter.convert_mgf(input_mgf, args.output_mgf, compound_scan_mapping)
    elif args.toolname == "MZTABM":
        print("MZTABM")
        workflow_parameters = proteosafe.parse_xml_file(args.workflowParameters)
        mangled_mapping = proteosafe.get_mangled_file_mapping(workflow_parameters)

        name_mangle_mapping = {}
        for key in mangled_mapping:
            demangled_name = mangled_mapping[key]
            name_mangle_mapping[os.path.basename(demangled_name)] = os.path.join(args.input_spectra_folder, key)

        compound_filename_mapping = mztabm_formatter.convert_to_feature_csv(args.quantification_table, args.quantification_table_reformatted)
        mztabm_formatter.create_mgf(input_filenames, args.output_mgf, compound_filename_mapping, name_mangle_mapping=name_mangle_mapping)

    # Finally, we can renormlize the output
    try:
        if args.QUANT_FILE_NORM == "RowSum":
            quant_df = pd.read_csv(args.quantification_table_reformatted, sep=",")
            for column in quant_df:
                if "Peak area" in column:
                    quant_df[column] = quant_df[column] / max(quant_df[column]) * 1000000

            quant_df.to_csv(args.quantification_table_reformatted, sep=",", index=False)
    except:
        pass

if __name__ == "__main__":
    main()

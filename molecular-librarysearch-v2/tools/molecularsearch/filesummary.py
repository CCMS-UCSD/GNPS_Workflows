#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import uuid
from collections import defaultdict
import ming_proteosafe_library
import ming_fileio_library
import ming_parallel_library
import csv
import re


def summary_wrapper(search_param_dict):
    summary_files(search_param_dict["spectrum_file"], search_param_dict["tempresults_folder"], search_param_dict["args"])

def summary_files(spectrum_file, tempresults_folder, args):
    summary_filename = os.path.join(tempresults_folder, os.path.basename(spectrum_file) + ".summary")
    cmd = "%s %s -x \"run_summary delimiter=tab\" > %s" % (args.msaccess_binary, spectrum_file, summary_filename)
    print(cmd)
    os.system(cmd)




def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('spectra_folder', help='spectrafolder')
    parser.add_argument('workflow_parameters', help='output folder for parameters')
    parser.add_argument('result_file', help='output folder for parameters')
    parser.add_argument('msaccess_binary', help='output folder for parameters')
    parser.add_argument('--parallelism', default=1, type=int, help='Parallelism')
    args = parser.parse_args()


    params_object = ming_proteosafe_library.parse_xml_file(open(args.workflow_parameters))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_object)
    spectra_files = ming_fileio_library.list_files_in_dir(args.spectra_folder)

    spectra_files.sort()


    tempresults_folder = "tempresults"
    try:
        os.mkdir(tempresults_folder)
    except:
        print("folder error")

    parameter_list = []
    for spectrum_file in spectra_files:
        param_dict = {}
        param_dict["spectrum_file"] = spectrum_file
        param_dict["tempresults_folder"] = tempresults_folder
        param_dict["args"] = args

        parameter_list.append(param_dict)

    #for param_dict in parameter_list:
    #    search_wrapper(param_dict)
    print("Parallel to execute", len(parameter_list))
    ming_parallel_library.run_parallel_job(summary_wrapper, parameter_list, 10)


    """Merging Files and adding full path"""
    all_result_files = ming_fileio_library.list_files_in_dir(tempresults_folder)
    full_result_list = []
    for input_file in all_result_files:
        try:
            result_list = ming_fileio_library.parse_table_with_headers_object_list(input_file)
            for result in result_list:
                output_dict = {}
                output_dict["Filename"] = result["Filename"]
                output_dict["Vendor"] = result["Vendor"]
                output_dict["Model"] = result["Model"]
                output_dict["MS1s"] = result["MS1s"]
                output_dict["MS2s"] = result["MS2s"]
                full_result_list.append(output_dict)
        except:
            #raise
            print("Error", input_file)

        #print(result_list)
        #full_result_list += result_list

    for result_object in full_result_list:
        mangled_name = os.path.basename(result_object["Filename"])
        full_path = mangled_mapping[mangled_name]
        result_object["full_CCMS_path"] = full_path

    ming_fileio_library.write_list_dict_table_data(full_result_list, args.result_file)





if __name__ == "__main__":
    main()

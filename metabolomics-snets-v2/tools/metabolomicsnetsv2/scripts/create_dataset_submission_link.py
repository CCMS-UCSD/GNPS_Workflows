#!/usr/bin/python

import sys
import getopt
import os
import json
import requests
import pandas as pd
import ming_proteosafe_library

def main():
    input_parameters_xml = sys.argv[1]
    output_filename = sys.argv[2]

    param_obj = ming_proteosafe_library.parse_xml_file(open(input_parameters_xml))

    print(param_obj.keys())

    peak_list_list = []
    metadata_list = []

    if "spec_on_server" in param_obj:
        peak_list_list += (param_obj["spec_on_server"])
    if "spec_on_server_group2" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group2"])
    if "spec_on_server_group3" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group3"])
    if "spec_on_server_group4" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group4"])
    if "spec_on_server_group5" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group5"])
    if "spec_on_server_group6" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group6"])
    if "spec_on_server_group6" in param_obj:
        peak_list_list += (param_obj["spec_on_server_group6"])
    if "metadatafile" in param_obj:
        metadata_list += (param_obj["metadatafile"])

    params_dict = {}
    params_dict["desc"] = "GNPS - Data for Analysis For GNPS Job " + param_obj["task"][0]
    params_dict["workflow"] = "MASSIVE-COMPLETE"
    params_dict["peak_list_files"] = ";".join(peak_list_list)
    params_dict["other_files"] = ";".join(metadata_list)

    output_file = open(output_filename, "w")
    output_file.write("filenames\tmetadatanames\ttask\n")
    output_file.write(";".join(peak_list_list))
    output_file.write("\t")
    output_file.write(";".join(metadata_list))
    output_file.write("\t")
    output_file.write(param_obj["task"][0])
    output_file.write("\n")

if __name__ == "__main__":
    main()
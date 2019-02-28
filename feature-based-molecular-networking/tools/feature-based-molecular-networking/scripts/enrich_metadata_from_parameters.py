#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import ming_fileio_library
import ming_proteosafe_library
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('proteosafe_parameters', help='proteosafe_parameters')
    parser.add_argument('metadata_folder', help='metadata_folder')
    parser.add_argument('output_metadata_file', help='output_metadata_file')
    args = parser.parse_args()

    param_obj = ming_proteosafe_library.parse_xml_file(open(args.proteosafe_parameters))

    mangled_file_mapping = ming_proteosafe_library.get_mangled_file_mapping(param_obj)

    default_group_mapping = defaultdict(list)
    file_to_group_mapping = {}
    for mangled_name in mangled_file_mapping:
        if mangled_name.find("specone-") != -1:
            default_group_mapping["G1"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G1"
        if mangled_name.find("spectwo-") != -1:
            default_group_mapping["G2"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G2"
        if mangled_name.find("specthree-") != -1:
            default_group_mapping["G3"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G3"
        if mangled_name.find("specfour-") != -1:
            default_group_mapping["G4"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G4"
        if mangled_name.find("specfive-") != -1:
            default_group_mapping["G5"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G5"
        if mangled_name.find("specsix-") != -1:
            default_group_mapping["G6"].append(mangled_file_mapping[mangled_name])
            file_to_group_mapping[os.path.basename(mangled_file_mapping[mangled_name])] = "G6"

    metadata_files_in_folder = ming_fileio_library.list_files_in_dir(args.metadata_folder)

    row_count = 0
    table_data = defaultdict(list)
    if len(metadata_files_in_folder) == 1:
        row_count, table_data = ming_fileio_library.parse_table_with_headers(metadata_files_in_folder[0])

    print(table_data)
    for key in table_data:
        print(key, len(table_data[key]))

    for i in range(row_count):
        print(i)
        filename = table_data["filename"][i]
        if len(filename) < 2:
            continue
        print(filename, filename[0], filename[-1])

        if filename[0] == "\"":
            filename = filename[1:]
        if filename[-1] == "\"":
            filename = filename[:-1]

        table_data["filename"][i] = filename

        basename_filename = os.path.basename(filename)
        group_name = "NoDefaultGroup"
        if basename_filename in file_to_group_mapping:
            group_name = file_to_group_mapping[basename_filename]
        table_data["ATTRIBUTE_DefaultGroup"].append(group_name)



    for input_filename in file_to_group_mapping:
        if input_filename in table_data["filename"]:
            continue
        else:
            for key in table_data:
                if key != "ATTRIBUTE_DefaultGroup" and key != "filename":
                    table_data[key].append("N/A")

            table_data["ATTRIBUTE_DefaultGroup"].append(file_to_group_mapping[input_filename])
            table_data["filename"].append(input_filename)

    ming_fileio_library.write_dictionary_table_data(table_data, args.output_metadata_file)












if __name__ == "__main__":
    main()

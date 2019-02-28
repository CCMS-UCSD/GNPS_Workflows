#!/usr/bin/python

import sys
import getopt
import os
import argparse
import ming_fileio_library

from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Creates alan table')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('output_filename', help='output_filename')
    args = parser.parse_args()

    print(args.input_clusterinfosummary)

    data_list = ming_fileio_library.parse_table_with_headers_object_list(args.input_clusterinfosummary)

    all_filenames = []
    for data_object in data_list:
        if "UniqueFileSources" in data_object:
            all_filenames += data_object["UniqueFileSources"].split("|")
        else:
            filenames = list(set([filename.split(":")[0] for filename in data_object["AllFiles"].split("###") if len(filename) > 2]))
            all_filenames += filenames

    all_filenames = list(set(all_filenames))

    compounds_to_files = defaultdict(list)
    for data_object in data_list:
        filenames = []
        if "UniqueFileSources" in data_object:
            filenames = data_object["UniqueFileSources"].split("|")
        else:
            filenames = list(set([filename.split(":")[0] for filename in data_object["AllFiles"].split("###") if len(filename) > 2]))
        compound_name = data_object["LibraryID"]
        compounds_to_files[compound_name] += filenames

    output_list = []
    for compound_name in compounds_to_files:
        output_dict = {}
        output_dict["LibraryID"] = compound_name
        output_dict["TotalFiles"] = len(compounds_to_files[compound_name])
        for filename in compounds_to_files[compound_name]:
            output_dict[filename] = "1"

        for filename in all_filenames:
            if not filename in output_dict:
                output_dict[filename] = "0"

        output_list.append(output_dict)

    ming_fileio_library.write_list_dict_table_data(output_list, args.output_filename)




if __name__ == "__main__":
    main()

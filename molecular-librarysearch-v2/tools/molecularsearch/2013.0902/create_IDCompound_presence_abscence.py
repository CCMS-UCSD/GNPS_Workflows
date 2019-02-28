#!/usr/bin/python

import sys
import getopt
import os
import argparse
from collections import defaultdict
import ming_fileio_library

def main():
    parser = argparse.ArgumentParser(description='Creates alan table')
    parser.add_argument('input_identifications_filename', help='input_identifications_filename')
    parser.add_argument('output_filename', help='output_filename')
    args = parser.parse_args()

    print(args.input_identifications_filename)

    data_list = ming_fileio_library.parse_table_with_headers_object_list(args.input_identifications_filename)

    all_filenames = set()
    compounds_to_files = defaultdict(set)
    for data_object in data_list:
        query_filename = "f." + data_object["full_CCMS_path"]
        compound_name = data_object["Compound_Name"]
        all_filenames.add(query_filename)
        compounds_to_files[compound_name].add(query_filename)

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

#!/usr/bin/python


import sys
import getopt
import os
import json
import ming_fileio_library
from collections import defaultdict

def usage():
    print("<input intermediate folder> <output protein coverage file>")


def main():
    input_intermediate_folder = sys.argv[1]
    output_filename = sys.argv[2]

    all_protein_stats = {}

    #Creating a command line for each partition
    all_intermediate_files = ming_fileio_library.list_files_in_dir(input_intermediate_folder)
    output_list = []
    for parallel_output_filename in all_intermediate_files:
        result_list = ming_fileio_library.parse_table_with_headers_object_list(parallel_output_filename)
        output_list += result_list

    ming_fileio_library.write_list_dict_table_data(output_list, output_filename)


if __name__ == "__main__":
    main()

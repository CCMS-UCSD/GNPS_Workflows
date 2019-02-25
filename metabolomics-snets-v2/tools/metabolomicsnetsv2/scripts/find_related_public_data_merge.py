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
    output_map = defaultdict(list)
    for parallel_output_filename in all_intermediate_files:
        row_count, table_data = ming_fileio_library.parse_table_with_headers(parallel_output_filename)
        for key in table_data:
            output_map[key] += table_data[key]

    ming_fileio_library.write_dictionary_table_data(output_map, output_filename)


if __name__ == "__main__":
    main()

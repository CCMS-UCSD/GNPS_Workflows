#!/usr/bin/python


import sys
import getopt
import os
import ming_fileio_library
from collections import defaultdict

def usage():
    print "<input folder> <output tsv file>"




def main():
    input_folder_path = sys.argv[1]
    output_tsv = sys.argv[2]

    files = ming_fileio_library.list_files_in_dir(input_folder_path)

    merged_dict = defaultdict(list)

    for input_file in files:
        print("loading", input_file)
        row_count, table_data = ming_fileio_library.parse_table_with_headers(input_file)
        for key in table_data:
            merged_dict[key] += table_data[key]

    ming_fileio_library.write_dictionary_table_data(merged_dict, output_tsv)

if __name__ == "__main__":
    main()

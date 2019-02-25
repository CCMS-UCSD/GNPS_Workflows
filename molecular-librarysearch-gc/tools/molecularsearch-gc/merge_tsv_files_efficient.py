#!/usr/bin/python


import sys
import getopt
import os
import ming_fileio_library
from collections import defaultdict

def usage():
    print("<input folder> <output file>")



def main():
    input_files_list = ming_fileio_library.list_files_in_dir(sys.argv[1])

    output_dict = defaultdict(list)
    output_file = open(sys.argv[2], "w")

    file_count = 0
    for input_file in input_files_list:
        row_count = 0
        for line in open(input_file):
            if file_count == 0 and row_count == 0:
                output_file.write(line)
            elif row_count != 0:
                output_file.write(line)

            row_count += 1

        file_count += 1

    output_file.close()




if __name__ == "__main__":
    main()

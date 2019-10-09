#!/usr/bin/python


import sys
import getopt
import os
import json
import requests
import ming_fileio_library


def get_metadata_information_per_filename(filename):
    url = "https://redu.ucsd.edu/filename?query=%s" % (filename)
    r = requests.get(url)
    
    return r.json()


def main():
    results_filename = sys.argv[1]
    output_filename = sys.argv[2]

    input_results = ming_fileio_library.parse_table_with_headers_object_list(results_filename)
    output_results = []

    #Check if server is up

    for result_object in input_results:
        filename = result_object["filename"]
        get_metadata_information_per_filename(filename)


    ming_fileio_library.write_list_dict_table_data(output_results, output_filename)


if __name__ == "__main__":
    main()

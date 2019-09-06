#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import uuid
from collections import defaultdict
import ming_fileio_library




def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('filestats', help='filestats')
    parser.add_argument('dbresults', help='dbresults')
    parser.add_argument('output_filestats', help='output folder for parameters')
    args = parser.parse_args()

    identified_spectra_in_filename = defaultdict(set)

    all_identifications = ming_fileio_library.parse_table_with_headers_object_list(args.dbresults)
    for identification in all_identifications:
        filename = identification["full_CCMS_path"]
        scan = identification["#Scan#"]

        identified_spectra_in_filename[filename].add(scan)

    print(identified_spectra_in_filename)

    output_list = []
    file_summaries = ming_fileio_library.parse_table_with_headers_object_list(args.filestats)

    for file_summary in file_summaries:
        filename = file_summary["full_CCMS_path"]
        count = len(identified_spectra_in_filename[filename])
        file_summary["identified_ms2"] = count
        percent_identified = 0
        try:
            percent_identified = float(count) / float(file_summary["MS2s"])
        except:
            percent_identified = 0

        file_summary["percent_identified"] = percent_identified
        output_list.append(file_summary)

    ming_fileio_library.write_list_dict_table_data(output_list, args.output_filestats)





if __name__ == "__main__":
    main()

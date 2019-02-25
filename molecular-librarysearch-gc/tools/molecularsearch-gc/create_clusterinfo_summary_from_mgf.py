#!/usr/bin/python


import sys
import getopt
import os
import ming_spectrum_library
import ming_fileio_library

def main():
    parameters_filename = sys.argv[1]
    input_mgf_filename = sys.argv[2]
    output_clusterinfosummary = sys.argv[3]

    output_list = []

    spectrum_collection = ming_spectrum_library.SpectrumCollection(input_mgf_filename)
    spectrum_collection.load_from_file()

    for spectrum in spectrum_collection.spectrum_list:
        output_dict = {}
        output_dict["cluster index"] = spectrum.scan
        output_dict["RTMean"] = spectrum.retention_time
        output_list.append(output_dict)

    ming_fileio_library.write_list_dict_table_data(output_list, output_clusterinfosummary)












if __name__ == "__main__":
    main()

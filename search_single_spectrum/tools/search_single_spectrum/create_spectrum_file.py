#!/usr/bin/python


import sys
import getopt
import os
import math
import ming_spectrum_library
import json
import ming_gnps_library
import spectrum_alignment
import ming_proteosafe_library
import ming_parallel_library
import ming_fileio_library
import masst_validator

def usage():
    print("<param.xml> <output mgf file>")


def main():
    paramxml_input_filename = sys.argv[1]
    output_mgf_file = sys.argv[2]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    #Validating the spectrum string
    if masst_validator.validate(param_obj["spectrum_string"][0], int(param_obj["MIN_MATCHED_PEAKS"][0])) != 0:
        print("Validation Error on Input")
        exit(1)

    spectrum_collection = get_spectrum_collection_from_param_obj(params_obj)
    spectrum_collection.save_to_mgf(open(output_mgf_file, "w"))


def get_spectrum_collection_from_param_obj(param_obj):
    precursor_mz = float(param_obj["precursor_mz"][0])
    spectrum_string = param_obj["spectrum_string"][0]
    peaks_lines = spectrum_string.split("\n")
    peak_list = []
    for peak_line in peaks_lines:
        splits = peak_line.split()
        mass = float(splits[0])
        intensity = float(splits[1])
        peak_list.append([mass, intensity])

    peak_list = sorted(peak_list, key=lambda peak: peak[0])

    spectrum_obj = ming_spectrum_library.Spectrum("search_spectrum.mgf", 1, 0, peak_list, precursor_mz, 1, 2)
    spectrum_collection = ming_spectrum_library.SpectrumCollection("search_spectrum.mgf")

    spectrum_collection.spectrum_list = [spectrum_obj]

    return spectrum_collection


if __name__ == "__main__":
    main()

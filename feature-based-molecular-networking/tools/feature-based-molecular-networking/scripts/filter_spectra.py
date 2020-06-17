#!/usr/bin/python

import sys
import getopt
import argparse
import ming_spectrum_library

parser = argparse.ArgumentParser(description='Filter Spectra')
parser.add_argument('input_mgf_filename', help='input_mgf_filename')
parser.add_argument('output_mgf_filename', help='output_mgf_filename')
parser.add_argument('--FILTER_PRECURSOR_WINDOW', help='0', default=None)
parser.add_argument('--WINDOW_FILTER', help='0', default=None)
args = parser.parse_args()

# Load the spectra
spectrum_collection = ming_spectrum_library.SpectrumCollection(args.input_mgf_filename)
spectrum_collection.load_from_mgf()

# Applying the Filtering
if args.FILTER_PRECURSOR_WINDOW == "1":
    for spectrum in spectrum_collection.spectrum_list:
        if spectrum is not None:
            spectrum.window_filter_peaks(50, 6)

if args.FILTER_PRECURSOR_WINDOW == "1":
    for spectrum in spectrum_collection.spectrum_list:
        if spectrum is not None:
            spectrum.filter_precursor_peaks()

# Saving Spectra
spectrum_collection.save_to_mgf(open(args.output_mgf_filename, "w"))

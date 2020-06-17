#!/usr/bin/python

import sys
import getopt
import argparse
import ming_spectrum_library

parser = argparse.ArgumentParser(description='Filter Spectra')
parser.add_argument('input_mgf_filename', help='input_mgf_filename')
parser.add_argument('output_mgf_filename', help='output_mgf_filename')
parser.add_argument('output_filtered_mgf_filename', help='output_filtered_mgf_filename')
parser.add_argument('--FILTER_PRECURSOR_WINDOW', help='0', default=None)
parser.add_argument('--WINDOW_FILTER', help='0', default=None)
args = parser.parse_args()

# Load the spectra
spectrum_collection = ming_spectrum_library.SpectrumCollection(args.input_mgf_filename)
spectrum_collection.load_from_mgf()

# Making sure to renumber
spectrum_list = sorted(spectrum_collection.spectrum_list, key=lambda spectrum: int(spectrum.scan))

included_scans = set()
spectrum_dict = {}
for spectrum in spectrum_list:
    spectrum_dict[int(spectrum.scan)] = spectrum
    included_scans.add(int(spectrum.scan))

max_scan = max(included_scans)

output_spectrum_list = []
for scan_count in range(1, max_scan+1):
    if scan_count in spectrum_dict:
        output_spectrum_list.append(spectrum_dict[scan_count])
    else:
        output_spectrum_list.append(ming_spectrum_library.Spectrum(args.output_mgf_filename, scan_count, scan_count-1, [], 0.0, 1, 2))

spectrum_collection.spectrum_list = output_spectrum_list
# Saving out unfiltered spectra
spectrum_collection.save_to_mgf(open(args.output_mgf_filename, "w"), renumber_scans=False)

# Applying the Filtering
if args.FILTER_PRECURSOR_WINDOW == "1":
    for spectrum in spectrum_collection.spectrum_list:
        if spectrum is not None:
            spectrum.window_filter_peaks(50, 6)

if args.FILTER_PRECURSOR_WINDOW == "1":
    for spectrum in spectrum_collection.spectrum_list:
        if spectrum is not None:
            spectrum.filter_precursor_peaks()

# Saving out Filtered Spectra
spectrum_collection.save_to_mgf(open(args.output_filtered_mgf_filename, "w"), renumber_scans=False)

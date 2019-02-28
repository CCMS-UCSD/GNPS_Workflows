#!/usr/bin/python

import sys
import getopt
from shutil import copyfile

import ming_spectrum_library

input_mgf_filename = sys.argv[1]
output_mgf_filename = sys.argv[2]

spectrum_collection = ming_spectrum_library.SpectrumCollection(input_mgf_filename)
spectrum_collection.load_from_mgf()

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
        output_spectrum_list.append(ming_spectrum_library.Spectrum(output_mgf_filename, scan_count, scan_count-1, [], 0.0, 1, 2))


spectrum_collection.spectrum_list = output_spectrum_list

spectrum_collection.save_to_mgf(open(output_mgf_filename, "w"))


print(included_scans)
#copyfile(sys.argv[1], sys.argv[2])

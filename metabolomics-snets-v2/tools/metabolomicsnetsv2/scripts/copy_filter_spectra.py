import shutil
import sys
import os
import argparse
import pandas as pd
import ming_spectrum_library


parser = argparse.ArgumentParser(description='Copy or filter')
parser.add_argument("inputspectrafolder")
parser.add_argument("output_filename")
parser.add_argument("groupsfilename")
parser.add_argument("clusterinfofilename")
parser.add_argument("--filterg6", default="0")

args = parser.parse_args()

print(args)

input_specs_ms = os.path.join(args.inputspectrafolder, "specs_ms.mgf")

if args.filterg6 == "0":
    shutil.copyfile(input_specs_ms, args.output_filename)
    exit(0)

#Doing the filtering
clusterinfo_df = pd.read_csv(args.clusterinfofilename, sep="\t")

files_to_filter = []
for line in open(args.groupsfilename):
    if line.split("=")[0] == "GROUP_G6":
        files_to_filter = line.split("=")[1].split(";")
        files_to_filter = [filename.rstrip() for filename in files_to_filter]

print("files_to_filter", files_to_filter)

filtered_clusterinfo_df = clusterinfo_df[clusterinfo_df["#Filename"].isin(files_to_filter)]
clusters_to_filter = set(list(filtered_clusterinfo_df["#ClusterIdx"]))

print("clusters_to_filter", clusters_to_filter)

#Loading the spectra
spectrum_collection = ming_spectrum_library.SpectrumCollection(input_specs_ms)
spectrum_collection.load_from_mgf()


filtered_spectrum_list = []
for spectrum in spectrum_collection.spectrum_list:
    if spectrum is None:
        continue
    else:
        scan = spectrum.scan
        if scan in clusters_to_filter:
            continue
        else:
            filtered_spectrum_list.append(spectrum)

#Renumbering to make sure empty ones are still there
included_scans = set()
spectrum_dict = {}
for spectrum in filtered_spectrum_list:
    spectrum_dict[int(spectrum.scan)] = spectrum
    included_scans.add(int(spectrum.scan))

max_scan = max(included_scans)

output_spectrum_list = []
for scan_count in range(1, max_scan+1):
    if scan_count in spectrum_dict:
        output_spectrum_list.append(spectrum_dict[scan_count])
    else:
        output_spectrum_list.append(ming_spectrum_library.Spectrum(args.output_filename, scan_count, scan_count-1, [], 0.0, 1, 2))

spectrum_collection.spectrum_list = output_spectrum_list

spectrum_collection.save_to_mgf(open(args.output_filename, "w"), renumber_scans=False)

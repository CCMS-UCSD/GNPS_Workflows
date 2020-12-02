#!/usr/bin/python

import pandas as pd
import sys
import getopt
import os
import argparse
import subprocess
import ming_fileio_library
import proteosafe
from collections import defaultdict

def parse_peaks_for_output(input_filename, output_filename):
    output_file = open(output_filename, "w")

    db_number = -1
    rt_seconds = -1
    num_peaks_detected = False
    for line in open(input_filename):
        if line.find("Name:") != -1:
            rt_seconds = float(line.split("time_")[1].split("_min")[0]) * 60
            continue
        if line.find("DB#") != -1:
            db_number = int(line.split(" ")[-1])
            continue
        if line.find("Num Peaks") != -1:
            num_peaks_detected = True
            continue
        if len(line) > 3 and num_peaks_detected == True:
            all_peaks = []
            num_peaks_detected = False
            splits = line.rstrip().split(";")
            for split in splits:
                peak_splits = split.lstrip().rstrip().split(" ")
                mass = float(int(float(peak_splits[0])))
                intensity = float(peak_splits[1]) * 100000
                all_peaks.append([str(mass), str(intensity)])
            #Write output
            output_file.write("BEGIN IONS\n")
            output_file.write("PEPMASS=0\n")
            output_file.write("RTINSECONDS=%f\n" % (rt_seconds))
            output_file.write("SCANS=%d\n" % (db_number))
            output_file.write("CHARGE=0\n")
            output_file.write("MSLEVEL=2\n")


            for peak in all_peaks:
                output_file.write(" ".join(peak) + "\n")

            output_file.write("END IONS\n")

    output_file.close()


""" Presence and Abscence of features across many files
    Need to fix this for clustering
"""
def simple_presence_of_merged_spectra_processing(input_integrals_filename, output_clusterinfo_filename, mangled_mapping):
    extension_stripped_mangled_mapping = {}
    for key in mangled_mapping:
        without_ext = ming_fileio_library.get_filename_without_extension(key)
        extension_stripped_mangled_mapping[without_ext] = mangled_mapping[key]


    header_order = open(input_integrals_filename).readline().rstrip().split(",")[1:]

    table_list = ming_fileio_library.parse_table_with_headers_object_list(input_integrals_filename, delimiter=",")
    #Removing other header infroamtion
    table_list = table_list[2:]

    output_dict = defaultdict(list)

    print("for zheng's sanity print the wholetable ----")
    print(table_list)
    for result_object in table_list:
        try:
            sample_name = result_object["RTS:"]
        except:
            sample_name = "unknown"
        scan_number = 0
        for header in header_order:
            scan_number += 1
            abundance = result_object[header]
            output_dict["filename"].append( sample_name )
            output_dict["abundance"].append( abundance )
            output_dict["scan_number"].append( scan_number )
            output_dict["RT"].append( header )

    ming_fileio_library.write_dictionary_table_data(output_dict, output_clusterinfo_filename)

# Parsing the quant table
def generate_clustersummary(input_integrals_filename, output_clustersummary_filename):
    df = pd.read_csv(input_integrals_filename, nrows=20)
    scan_numbers = list(df.columns)
    rts_list = list(df.iloc[0])

    output_list = []
    for i, scan in enumerate(scan_numbers):
        if i == 0:
            continue

        output_dict = {}
        output_dict["cluster index"] = scan
        output_dict["RTMean"] = rts_list[i].split(" ")[0]
        output_dict["Balance Score"] = rts_list[i].split(" ")[-1].replace("(", "").replace(")", "").replace("%", "")

        output_list.append(output_dict)

    output_df = pd.DataFrame(output_list)
    output_df.to_csv(output_clustersummary_filename, sep='\t', index=False)

def determine_filetype_of_import(input_folder):
    input_filenames = ming_fileio_library.list_files_in_dir(input_folder)
    ext = ming_fileio_library.get_filename_extension(input_filenames[0])

    if ext.upper() == ".CDF":
        return "netcdf"

    if ext.upper() == ".MZXML":
        return "mzxml"

    if ext.upper() == ".MZML":
        return "mzml"

    print("Unsupported extension")
    exit(1)

# def cluster_spectra(clustered_mgf, clustersummary, RT_TOLERANCE):
#     spectrum_collection = ming_spectrum_library.SpectrumCollection(clustered_mgf)
#     spectrum_collection.load_from_mgf()
#
#     cluster_list = ming_fileio_library.parse_table_with_headers_object_list(clustersummary)
#
#     for spectrum in spectrum_collection.spectrum_list:
#         scan = spectrum.scan
#         for result_object in cluster_list:
#             if result_object["cluster index"] == str(scan):
#                 spectrum.retention_time = float(result_object["RTMean"])
#
#     spectrum_list = spectrum_collection.spectrum_list
#
#     """Need to make this do a proper optimziation"""
#     output_spectrum_list = []
#     output_result_list = []
#     for i in range(len(spectrum_list) - 1):
#         spectrum_first = spectrum_list[i]
#         spectrum_second = spectrum_list[i + 1]
#
#         similarity = spectrum_first.cosine_spectrum(spectrum_second, 1.0)
#
#         if abs(spectrum_first.retention_time - spectrum_second.retention_time) < RT_TOLERANCE and similarity > 0.9:
#             output_spectrum_list.append(spectrum_first)
#             output_result_list.append(cluster_list[i])
#             i += 1
#         else:
#             output_spectrum_list.append(spectrum_first)
#             output_result_list.append(cluster_list[i])
#
#
#     spectrum_collection.spectrum_list = output_spectrum_list
#     spectrum_collection.save_to_mgf(open(clustered_mgf, "w"))
#
#     ming_fileio_library.write_list_dict_table_data(output_result_list, clustersummary)

def main():
    parser = argparse.ArgumentParser(description='Processing and feature detecting all gc files')
    parser.add_argument('proteosafe_parameters', help='proteosafe_parameters')
    parser.add_argument('spectrum_folder', help='spectrum_folder')
    parser.add_argument('scratch_folder', help='scratch_folder')
    parser.add_argument('clustered_mgf', help='scratch_folder')
    parser.add_argument('clusterinfo', help='scratch_folder')
    parser.add_argument('clustersummary', help='scratch_folder')
    parser.add_argument('summary_output', help='summary_output')
    parser.add_argument('python_runtime', help='python_runtime')
    parser.add_argument('-import_script', help='import_script', default="./proc/io/importmsdata.py")
    parser.add_argument('-align_script', help='align_script', default="./proc/preproc/intrapalign.py")
    parser.add_argument('-noise_script', help='noise_script', default="./proc/preproc/noisefilter.py")
    parser.add_argument('-interalign_script', help='interalign_script', default="./proc/preproc/interpalign.py")
    parser.add_argument('-peakdetect_script', help='peakdetect_script', default="./proc/preproc/peakdetect.py")
    parser.add_argument('-export_script', help='export_script', default="./proc/io/export.py")
    parser.add_argument('-report_script', help='report_script', default="./proc/io/report.py")
    parser.add_argument('-vistic_script', help='vistic_script', default="./proc/vis/vistic.py")
    args = parser.parse_args()

    workflow_params = proteosafe.parse_xml_file(args.proteosafe_parameters)
    mangled_mapping = proteosafe.get_mangled_file_mapping(workflow_params)

    file_type_of_import = determine_filetype_of_import(args.spectrum_folder)


    hdf5_filename = os.path.join(args.scratch_folder, "data.h5")

    cmds = []

    #import data
    if workflow_params['TIME_UNIT'][0] == "MIN":
        cmds.append([args.python_runtime, args.import_script, "-f", file_type_of_import, args.spectrum_folder, hdf5_filename, "--timeunits", "'min'"])
    else:
        cmds.append([args.python_runtime, args.import_script, "-f", file_type_of_import, args.spectrum_folder, hdf5_filename, "--timeunits", "'sec'"])

    #intra align
    cmds.append([args.python_runtime, args.align_script, hdf5_filename, "--h5writepath", "'sp2D'"])

    #noisefilter
    cmds.append([args.python_runtime, args.noise_script, hdf5_filename, "--h5readpath", "'sp2D'", "--h5writepath", "'spproc2D'", "--window", "6", "--frame", "50"])

    #inter align
    cmds.append([args.python_runtime, args.interalign_script, hdf5_filename, "--h5readpath", "'spproc2D'", "--h5writepath", "'spal2D'"]) #According to ipython

    #peak detect
    cmds.append([args.python_runtime, args.peakdetect_script, hdf5_filename, "--h5readpath", "'spal2D'", "--individual", "no", "--frag_pattern", "deconvolution"])

    #output detection
    cmds.append([args.python_runtime, args.export_script, hdf5_filename, args.scratch_folder])

    #Additional outputs
    #python3 ./mshub/proc/io/export.py ./test.h5 --export_integral_table "yes" --export_ms_peak_list "yes" --logfile ./test.log --overwrite_logfile 'no'

    #outputting TIC with viz package
    #cmds.append([args.python_runtime, args.vistic_script, "--outputfile", os.path.join("..", args.tic_html), "--display", "no", hdf5_filename])
    cmds.append([args.python_runtime, args.report_script, "--output_prefix", "gnps-gc", hdf5_filename, "summary_temp"])
    cmds.append(["tar", "-cvf", os.path.join(args.summary_output, "summary.tar"), os.path.join("summary_temp", "gnps-gc")])


    for cmd in cmds:
        print(" ".join(cmd))
        subprocess.call(cmd)

    #Parse files
    output_peak_txt_filename = os.path.join(args.scratch_folder, "data_ms_peaks.txt")
    output_quant_filename = os.path.join(args.scratch_folder, "data_integrals.csv")

    # mapping the input spec names
    mangled_mapping_filename = {}
    for key , value in mangled_mapping.items():
        mangled_mapping_filename[key.split('.')[0]] = value.split('.')[0].split("/")[-1]

    f = open(output_quant_filename,'r').readlines()
    quant_in_memory = []
    for line in f:
        fname = line.split(',')[0]
        if fname.startswith("spec") and fname in mangled_mapping_filename:
            print("before:")
            print(line)
            line = line.replace(fname,mangled_mapping_filename[fname])
            print("after:")
            print(line)
        quant_in_memory.append(line)
    rewrite_quant = open(output_quant_filename,'w')
    rewrite_quant.write("".join(quant_in_memory))
    rewrite_quant.close()
    parse_peaks_for_output(output_peak_txt_filename, args.clustered_mgf)
    simple_presence_of_merged_spectra_processing(output_quant_filename, args.clusterinfo, mangled_mapping)
    generate_clustersummary(output_quant_filename, args.clustersummary)

    # Removing the big data
    os.remove(hdf5_filename)

    # if workflow_params["CLUSTER_SPECTRA"][0] == "YES":
    #     cluster_spectra(args.clustered_mgf, args.clustersummary, float(workflow_params["RT_TOLERANCE"][0]))


if __name__ == "__main__":
    main()

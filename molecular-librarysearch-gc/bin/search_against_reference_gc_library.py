#!/usr/bin/python

import sys
import getopt
import os
import math
import ming_fileio_library
import ming_proteosafe_library
import ming_spectrum_library
import json
import ming_gnps_library
import spectrum_alignment

try:
   import cPickle as pickle
except:
   import pickle

from collections import defaultdict

def usage():
    print "<param.xml> <input spectra folder (spectra)> <output clustered spectrum folder> <output matches file> <output datasets file>"

PATH_TO_DATASET_UPLOADS = "/data/ccms-data/uploads"

def load_identification_file_as_map(input_results_filename):
    print("Loading", input_results_filename)
    row_count, table_data = ming_fileio_library.parse_table_with_headers(input_results_filename)

    identification_map = {}

    for i in range(row_count):
        scan_number = int(table_data["#Scan#"][i])
        identification = table_data["Compound_Name"][i]
        spectrum_id = table_data["SpectrumID"][i]

        identification_dict = {}
        identification_dict["identification"] = identification
        identification_dict["spectrum_id"] = spectrum_id

        identification_map[scan_number] = identification_dict

    return identification_map

def finding_matches_in_public_data(input_spectra_filename, all_datasets, identification_dict):
    input_spectrum_collection = ming_spectrum_library.SpectrumCollection(input_spectra_filename)
    input_spectrum_collection.load_from_file()

    total_matches = 0

    search_parameters = []
    for dataset in all_datasets:
        dataset_id = dataset["dataset"]
        search_parameters.append({"dataset_id" : dataset_id, "input_spectrum_collection" : input_spectrum_collection, "identification_dict" : identification_dict})

    #Doing search serial
    search_results = []
    for search_param in search_parameters:
        #if total_matches > 0:
        #    continue
        print("SEARCHING " + str(search_param))
        dataset_matches = find_matches_in_dataset_wrapper(search_param)
        search_results.append(dataset_matches)
        total_matches += len(dataset_matches)

    print("datasets to consider: " + str(len(search_parameters)))

    #Parallel
    #search_results = ming_parallel_library.run_parallel_job(find_matches_in_dataset_wrapper, search_parameters, 10)

    #formatting output
    all_matches = []
    for i in range(len(search_results)):
        dataset_matches = search_results[i]

        print "outputting: " + str(search_parameters[i])

        all_matches += dataset_matches
    return all_matches


def find_matches_in_dataset_wrapper(parameters_dict):
    return find_matches_in_dataset(parameters_dict["dataset_id"], parameters_dict["input_spectrum_collection"], parameters_dict["identification_dict"])


def find_matches_in_dataset(dataset_id, input_spectrum_collection, identification_map):
    dataset_match_list = []
    path_to_peak_collection = os.path.join(PATH_TO_DATASET_UPLOADS, dataset_id, "peak")
    peak_files = ming_fileio_library.list_files_in_dir(path_to_peak_collection)

    for input_file in peak_files:
        print(input_file)
        relative_user_path_to_file = os.path.relpath(input_file, PATH_TO_DATASET_UPLOADS)
        reference_spectra = ming_spectrum_library.SpectrumCollection(input_file)
        reference_spectra.load_from_mzXML(drop_ms1=True)

        is_blank = 0
        if input_file.find("blank") != -1:
            is_blank = 1

        for myspectrum in input_spectrum_collection.spectrum_list:

            match_list = reference_spectra.search_spectrum(myspectrum, 1.0, 1.0, 4, 0.7, 1)
            for match in match_list:
                match_obj = {}
                match_obj["filename"] = relative_user_path_to_file
                match_obj["scan"] = match.scan
                match_obj["score"] = match.score
                match_obj["query_filename"] = match.query_filename
                match_obj["query_scan"] = match.query_scan
                match_obj["ppm_error"] = match.ppm_error
                match_obj["is_blank"] = is_blank
                match_obj["dataset_id"] = dataset_id

                #compound identification
                if match.scan in identification_map:
                    match_obj["identification"] = identification_map[match.scan]["identification"]
                    match_obj["spectrum_id"] = identification_map[match.scan]["spectrum_id"]
                else:
                    match_obj["identification"] = ""
                    match_obj["spectrum_id"] = ""

                dataset_match_list.append(match_obj)


    return dataset_match_list

def find_matches_in_library(query_spectrum_collection, library_list):
    peak_tolerance = 1.0
    for query_spectrum in query_spectrum_collection.spectrum_list:
        for library_spectrum in library_list:
            total_score, reported_alignments = spectrum_alignment.score_alignment(query_spectrum.peaks, library_spectrum.spectrum.peaks, 0, 0, peak_tolerance, 1)
            if total_score > 0.7:
                print(query_spectrum.filename, query_spectrum.scan, total_score, len(reported_alignments), library_spectrum.spectrumid)

def load_library_spectra(library_folder):
    library_spectra = []
    all_library_files = ming_fileio_library.list_files_in_dir(library_folder)
    for filename in all_library_files:
        temp_library_spectra = []
        extension = ming_fileio_library.get_filename_extension(filename)
        if extension == ".mgf":
            temp_library_spectra = ming_spectrum_library.load_gnps_library_mgf_file(filename)
        if extension == ".pkl":
            temp_library_spectra = pickle.load(open(filename, "rb"))
        library_spectra += temp_library_spectra
    return library_spectra

def load_query_spectra(query_spectrum_filename):
    spectrum_collection = ming_spectrum_library.SpectrumCollection(query_spectrum_filename)
    spectrum_collection.load_from_file()

    return spectrum_collection


def main():
    paramxml_input_filename = sys.argv[1]
    query_spectrum_filename = sys.argv[2]
    library_folder = sys.argv[3]
    output_identifications_filename = sys.argv[4]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    library_spectra = load_library_spectra(library_folder)
    query_spectrum_collection = load_query_spectra(query_spectrum_filename)

    print(len(library_spectra))
    print(len(query_spectrum_collection.spectrum_list))

    find_matches_in_library(query_spectrum_collection, library_spectra)





if __name__ == "__main__":
    main()

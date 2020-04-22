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
import trace_to_single_file
from collections import defaultdict

def usage():
    print("<param.xml> <parallel filename> <output matches file>")

PATH_TO_DATASET_UPLOADS = "/data/ccms-data/uploads"


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

"""Returns a map of dataset to a list of matches"""
def finding_matches_in_public_data(input_spectrum_collection, all_datasets, match_parameters):
    all_matches_to_datasets_map = {}

    dataset_search_parameters = []
    for dataset in all_datasets:
        if dataset["title"].upper().find("GNPS") == -1:
            continue
        dataset_id = dataset["dataset"]
        dataset_search_parameters.append({"dataset_id" : dataset_id, "input_spectrum_collection" : input_spectrum_collection, "match_parameters" : match_parameters})

    print("datasets to consider: " + str(len(dataset_search_parameters)))

    #Parallel
    search_results = ming_parallel_library.run_parallel_job(find_matches_in_dataset_wrapper, dataset_search_parameters, 50)

    #formatting output
    for i in range(len(search_results)):
        dataset_matches = search_results[i]
        dataset_id = dataset_search_parameters[i]["dataset_id"]
        all_matches_to_datasets_map[dataset_id] = { "matches" : dataset_matches}

    return all_matches_to_datasets_map


def find_matches_in_dataset_wrapper(parameters_dict):
    return find_matches_in_dataset(parameters_dict["dataset_id"], parameters_dict["input_spectrum_collection"], parameters_dict["match_parameters"])


def find_matches_in_dataset(dataset_id, input_spectrum_collection, match_parameters):
    if match_parameters["SEARCH_RAW"]:
        """Finding all data in ccms_peak collection"""
        path_to_ccms_peak = os.path.join("/data/massive/", dataset_id, "ccms_peak")
        #Recursive find file
        all_files = ming_fileio_library.list_all_files_in_directory(path_to_ccms_peak)
        #all_files = all_files[:1]
        print(all_files)

        all_matches = []
        for filename in all_files:
            size_of_file = os.path.getsize(filename)
            if size_of_file > 200 * 1024 * 1024:
                continue
            all_matches += find_matches_in_file(input_spectrum_collection, filename, filename.replace("/data/massive/", ""), match_parameters)

        return all_matches
    else:
        #Searching Clustered
        path_to_clustered_mgf = os.path.join(PATH_TO_DATASET_UPLOADS, "continuous", "clustered_data", dataset_id + "_specs_ms.mgf")
        relative_user_path_to_clustered = os.path.join("continuous", "clustered_data", dataset_id + "_specs_ms.mgf")
        return find_matches_in_file(input_spectrum_collection, path_to_clustered_mgf, relative_user_path_to_clustered, match_parameters, top_k=10000)

def find_matches_in_file(input_spectrum_collection, dataset_filepath, relative_dataset_filepath, match_parameters, top_k=1):
    dataset_match_list = []

    if not ming_fileio_library.is_path_present(dataset_filepath):
        print("Cant find", dataset_filepath)
        return dataset_match_list

    dataset_query_spectra = ming_spectrum_library.SpectrumCollection(dataset_filepath)
    try:
        dataset_query_spectra.load_from_file()
    except:
        return dataset_match_list

    # Parameterizing Analog Search Parameters
    analog_contraint_masses = []
    if match_parameters["ANALOG_CONSTRAINT"] == "BIOTRANSFORMATIONS":
        analog_contraint_masses.append(14) #TODO: Make this based on Louis' suggestion
    print(analog_contraint_masses)


    for repo_spectrum in dataset_query_spectra.spectrum_list:
        if match_parameters["FILTER_WINDOW"]:
            repo_spectrum.window_filter_peaks(50, 6)
        if match_parameters["FILTER_PRECURSOR"]:
            repo_spectrum.filter_precursor_peaks()

    for myspectrum in input_spectrum_collection.spectrum_list:
        if match_parameters["FILTER_WINDOW"]:
            myspectrum.window_filter_peaks(50, 6)
        if match_parameters["FILTER_PRECURSOR"]:
            myspectrum.filter_precursor_peaks()

        try:
            match_list = dataset_query_spectra.search_spectrum(myspectrum, 
                                                                match_parameters["PM_TOLERANCE"], 
                                                                match_parameters["FRAGMENT_TOLERANCE"], 
                                                                match_parameters["MIN_MATCHED_PEAKS"], 
                                                                match_parameters["MIN_COSINE"], 
                                                                analog_search=match_parameters["ANALOG_SEARCH"],
                                                                analog_constraint_masses=analog_contraint_masses,
                                                                top_k=top_k)
            for match in match_list:
                match["filename"] = relative_dataset_filepath
            dataset_match_list += match_list
        except:
            print("Error in Matching")

    print("Dataset matches: " + str(len(dataset_match_list)))

    return dataset_match_list

def get_parameters(params_obj):
    MIN_COSINE = 0.7
    MIN_MATCHED_PEAKS = 6
    PM_TOLERANCE = 2.0
    FRAGMENT_TOLERANCE = 2.0
    FILTER_PRECURSOR = True
    FILTER_WINDOW = True
    ANALOG_SEARCH = False
    ANALOG_CONSTRAINT = "NONE"
    SEARCH_RAW = False

    try:
        MIN_COSINE = float(params_obj["SCORE_THRESHOLD"][0])
    except:
        print("Param Not Found", "SCORE_THRESHOLD")

    try:
        MIN_MATCHED_PEAKS = int(params_obj["MIN_MATCHED_PEAKS"][0])
    except:
        print("Param Not Found", "MIN_MATCHED_PEAKS")

    try:
        PM_TOLERANCE = float(params_obj["tolerance.PM_tolerance"][0])
    except:
        print("Param Not Found", "PM_TOLERANCE")

    try:
        FRAGMENT_TOLERANCE = float(params_obj["tolerance.Ion_tolerance"][0])
    except:
        print("Param Not Found", "FRAGMENT_TOLERANCE")

    try:
        if params_obj["FILTER_PRECURSOR_WINDOW"][0] == "0":
            FILTER_PRECURSOR = False
    except:
        print("Param Not Found", "FILTER_PRECURSOR_WINDOW")

    try:
        if params_obj["WINDOW_FILTER"][0] == "0":
            FILTER_WINDOW = False
    except:
        print("Param Not Found", "WINDOW_FILTER")
    try:
        if params_obj["ANALOG_SEARCH"][0] == "1":
            ANALOG_SEARCH = True
    except:
        print("Param Not Found", "ANALOG_SEARCH")
    try:
        ANALOG_CONSTRAINT = params_obj["ANALOG_CONSTRAINT"][0]
    except:
        print("Param Not Found", "ANALOG_CONSTRAINT")
    try:
        if params_obj["SEARCH_RAW"][0] == "1":
            SEARCH_RAW = True
    except:
        print("Param Not Found", "SEARCH_RAW")

    parameters = {}
    parameters["MIN_COSINE"] = MIN_COSINE
    parameters["MIN_MATCHED_PEAKS"] = MIN_MATCHED_PEAKS
    parameters["PM_TOLERANCE"] = PM_TOLERANCE
    parameters["FRAGMENT_TOLERANCE"] = FRAGMENT_TOLERANCE
    parameters["FILTER_PRECURSOR"] = FILTER_PRECURSOR
    parameters["FILTER_WINDOW"] = FILTER_WINDOW
    parameters["ANALOG_SEARCH"] = ANALOG_SEARCH
    parameters["ANALOG_CONSTRAINT"] = ANALOG_CONSTRAINT
    parameters["SEARCH_RAW"] = SEARCH_RAW

    return parameters


"""Outputting all match summary for each dataset"""
def match_clustered(match_parameters, spectrum_collection, dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches):
    all_matches = finding_matches_in_public_data(spectrum_collection, all_datasets, match_parameters)

    """Resolving to File Level"""
    dataset_files_count = defaultdict(lambda: 0)
    output_source_list = []
    output_match_list = []

    MetaDataServerStatus = trace_to_single_file.test_metadata_server()

    for dataset in all_matches:
        for match_object in all_matches[dataset]["matches"]:
            dataset_accession = dataset_dict[dataset]["dataset"]
            dataset_scan = match_object["scan"]
            current_filelist, current_match_list = trace_to_single_file.trace_filename_filesystem(all_datasets, dataset_accession, dataset_scan, enrichmetadata=MetaDataServerStatus)
            output_source_list += current_filelist
            output_match_list += current_match_list

    seen_files = set()
    output_unique_source_list = []
    for output_file_object in output_source_list:
        dataset_accession = output_file_object["dataset_id"]
        dataset_filename = output_file_object["filename"]

        key = dataset_accession + ":" + dataset_filename
        if key in seen_files:
            continue

        dataset_files_count[dataset_accession] += 1

        seen_files.add(key)

        output_unique_source_list.append(output_file_object)

    ming_fileio_library.write_list_dict_table_data(output_unique_source_list, output_filename_unique_files)
    ming_fileio_library.write_list_dict_table_data(output_match_list, output_filename_all_matches)


    """ Summary """
    output_map = {"specs_filename" : [],"specs_scan" : [], "dataset_filename" : [], "dataset_scan" : [], "score" : [], "dataset_id" : [], "dataset_title" : [], "dataset_description" : [], "dataset_organisms" : [], "matchedpeaks" : [], "mzerror" : [], "files_count": []}
    for dataset in all_matches:
        #For each dataset, lets try to find the clustering information
        if len(all_matches[dataset]["matches"]) == 0:
            continue

        match_object = None

        #If it is more than one match, we need to consolidate
        if len(all_matches[dataset]["matches"]) > 1:
            sorted_match_list = sorted(all_matches[dataset]["matches"], key=lambda match: float(match["cosine"]), reverse=True)
            match_object = sorted_match_list[0]
        else:
            match_object = all_matches[dataset]["matches"][0]

        output_map['specs_filename'].append("specs_ms.mgf")
        output_map['specs_scan'].append(match_object["queryscan"])
        output_map['dataset_id'].append(dataset_dict[dataset]["dataset"])
        output_map['dataset_title'].append(dataset_dict[dataset]["title"])
        output_map['dataset_description'].append(dataset_dict[dataset]["description"].replace("\n", "").replace("\t", ""))
        output_map['dataset_organisms'].append( dataset_dict[dataset]["species"].replace("<hr class='separator'\/>", "!") )
        output_map['dataset_filename'].append(match_object["filename"])
        output_map['dataset_scan'].append(match_object["scan"])
        output_map['score'].append(match_object["cosine"])
        output_map['matchedpeaks'].append(match_object["matchedpeaks"])
        output_map['mzerror'].append(match_object["mzerror"])
        output_map['files_count'].append(dataset_files_count[dataset])


    ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)



def match_unclustered(match_parameters, spectrum_collection, dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches):
    MetaDataServerStatus = trace_to_single_file.test_metadata_server()

    all_matches_by_dataset = finding_matches_in_public_data(spectrum_collection, all_datasets, match_parameters)

    dataset_matches_output_list = []
    output_filename_unique_files_list = []
    output_filename_all_matches_list = []
    for dataset in all_matches_by_dataset:
        #For each dataset, lets try to find the clustering information
        if len(all_matches_by_dataset[dataset]["matches"]) == 0:
            continue

        top_match = sorted(all_matches_by_dataset[dataset]["matches"], key=lambda match: match["cosine"], reverse=True)[0]

        output_dict = {}
        output_dict['specs_filename'] = "specs_ms.mgf"
        output_dict['specs_scan'] = top_match["queryscan"]
        output_dict['dataset_id'] = dataset_dict[dataset]["dataset"]
        output_dict['dataset_title'] = dataset_dict[dataset]["title"]
        output_dict['dataset_description'] = dataset_dict[dataset]["description"].replace("\n", "").replace("\t", "")
        output_dict['dataset_organisms'] = dataset_dict[dataset]["species"].replace(";", "!")
        output_dict['dataset_filename'] = top_match["filename"]
        output_dict['dataset_scan'] = top_match["scan"]
        output_dict['score'] = top_match["cosine"]
        output_dict['matchedpeaks'] = top_match["matchedpeaks"]
        output_dict['mzerror'] = top_match["mzerror"]
        output_dict['files_count'] = len(all_matches_by_dataset[dataset]["matches"])

        dataset_matches_output_list.append(output_dict)


        """Unique Filenames Calculation"""
        unique_files = list(set([match["filename"] for match in all_matches_by_dataset[dataset]["matches"]]))
        for source_file in unique_files:
            output_object = {}
            output_object["dataset_id"] = dataset_dict[dataset]["dataset"]
            output_object["cluster_scan"] = ""
            output_object["filename"] = source_file
            output_object["metadata"] = ""

            if MetaDataServerStatus:
                metadata_list = trace_to_single_file.get_metadata_information_per_filename(source_file)
                output_object["metadata"] = "|".join(metadata_list)

            output_filename_unique_files_list.append(output_object)

        for match in all_matches_by_dataset[dataset]["matches"]:
            output_object = {}
            output_object["dataset_id"] = dataset
            output_object["cluster_scan"] = match["queryscan"]
            output_object["filename"] = match["filename"]
            output_object["filescan"] = match["scan"]
            output_object["metadata"] = ""

            if MetaDataServerStatus:
                metadata_list = trace_to_single_file.get_metadata_information_per_filename(match["filename"])
                output_object["metadata"] = "|".join(metadata_list)

            output_filename_all_matches_list.append(output_object)

    ming_fileio_library.write_list_dict_table_data(dataset_matches_output_list, output_matches_filename)
    ming_fileio_library.write_list_dict_table_data(output_filename_unique_files_list, output_filename_unique_files)
    ming_fileio_library.write_list_dict_table_data(output_filename_all_matches_list, output_filename_all_matches)

def main():
    paramxml_input_filename = sys.argv[1]
    parallel_param_filename = sys.argv[2]
    output_matches_filename = sys.argv[3]
    output_filename_unique_files = sys.argv[4]
    output_filename_all_matches = sys.argv[5]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    output_map = {"specs_filename" : [],"specs_scan" : [], "dataset_filename" : [], "dataset_scan" : [], "score" : [], "dataset_id" : [], "dataset_title" : [], "dataset_description" : [], "matchedpeaks" : [], "mzerror" : []}

    match_parameters = get_parameters(params_obj)

    try:
       if params_obj["FIND_MATCHES_IN_PUBLIC_DATA"][0] != "1":
           ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)
           exit(0)
    except:
       ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)
       exit(0)

    #If we are doing parallel
    partition_total = 1
    partition_of_node = 0
    params_map = json.loads(open(parallel_param_filename).read())
    partition_total = params_map["total_paritions"]
    partition_of_node = params_map["node_partition"]

    dataset_dict = params_map["dataset_dict"]
    all_datasets = params_map["all_datasets"]

    SEARCH_RAW = False
    try:
        if params_obj["SEARCH_RAW"][0] == "1":
            SEARCH_RAW = True
    except:
        print("Param Not Found", "SEARCH_RAW")

    """Matchign Clustered Data"""
    if SEARCH_RAW:
        match_unclustered(match_parameters, get_spectrum_collection_from_param_obj(params_obj), dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches)
    else:
        match_clustered(match_parameters, get_spectrum_collection_from_param_obj(params_obj), dataset_dict, all_datasets, output_matches_filename, output_filename_unique_files, output_filename_all_matches)



if __name__ == "__main__":
    main()

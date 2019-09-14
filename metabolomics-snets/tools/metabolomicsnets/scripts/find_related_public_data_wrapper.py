#!/usr/bin/python


import sys
import getopt
import os
import math
import ming_fileio_library
import ming_proteosafe_library
import ming_spectrum_library
import json
import ming_parallel_library
import ming_gnps_library
import molecular_network_library
import spectrum_alignment

def usage():
    print "<param.xml> <input spectra folder (spectra)> <output clustered spectrum folder> <output matches file> <output datasets file>"

PATH_TO_DATASET_UPLOADS = "/data/ccms-data/uploads"

def finding_matches_in_public_data(input_spectra_filename, all_datasets):

    all_matches_to_datasets_map = {}

    input_spectrum_collection = ming_spectrum_library.SpectrumCollection(input_spectra_filename)
    input_spectrum_collection.load_from_file()

    total_matches = 0

    search_parameters = []
    for dataset in all_datasets:
        if dataset["title"].upper().find("GNPS") == -1:
            continue
        dataset_id = dataset["dataset"]
        search_parameters.append({"dataset_id" : dataset_id, "input_spectrum_collection" : input_spectrum_collection})

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
    for i in range(len(search_results)):
        dataset_matches = search_results[i]
        dataset_id = search_parameters[i]["dataset_id"]

        print "outputting: " + str(search_parameters[i])

        all_matches_to_datasets_map[dataset_id] = { "matches" : dataset_matches}



    return all_matches_to_datasets_map


def find_matches_in_dataset_wrapper(parameters_dict):
    return find_matches_in_dataset(parameters_dict["dataset_id"], parameters_dict["input_spectrum_collection"])


def find_matches_in_dataset(dataset_id, input_spectrum_collection):
    dataset_match_list = []
    path_to_clustered_mgf = os.path.join(PATH_TO_DATASET_UPLOADS, dataset_id, "clustered", dataset_id + "_specs_ms.mgf")
    relative_user_path_to_clustered = os.path.join(dataset_id, "clustered", dataset_id + "_specs_ms.mgf")

    if not ming_fileio_library.is_path_present(path_to_clustered_mgf):
        return dataset_match_list

    #Lets compare these two files
    # input_spectra_filename and symlink_destination
    dataset_clustered_spectra = ming_spectrum_library.SpectrumCollection(path_to_clustered_mgf)
    dataset_clustered_spectra.load_from_file()

    for myspectrum in input_spectrum_collection.spectrum_list:
        match_list = dataset_clustered_spectra.search_spectrum(myspectrum, 1.0, 1.0, 6, 0.7, 1)
        for match in match_list:
            match.filename = relative_user_path_to_clustered
        dataset_match_list += match_list

    print "Dataset matches: " + str(len(dataset_match_list))

    return dataset_match_list


def main():
    paramxml_input_filename = sys.argv[1]
    parallel_param_filename = sys.argv[2]
    input_spectra_folder = sys.argv[3]
    library_search_results_filename = sys.argv[4]
    output_matches_filename = sys.argv[5]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    output_map = {"specs_filename" : [],"specs_scan" : [], "dataset_filename" : [], "dataset_scan" : [], "score" : [], "dataset_id" : [], "dataset_title" : [], "dataset_neighbors" : [], "Compound_Name" : [], "SpectrumID" : []}

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

    #print(len(all_datasets))
    #print(partition_of_node)
    #print(partition_total)

    #all_datasets = all_datasets[partition_of_node::partition_total]

    all_matches = finding_matches_in_public_data(os.path.join(input_spectra_folder, "specs_ms.mgf"), all_datasets)

    #Lets parse the search results and then populate this thing with search results
    library_search_result_count, library_search_data = ming_fileio_library.parse_table_with_headers(library_search_results_filename)
    scan_to_library_map = {}
    for i in range(library_search_result_count):
        scan = library_search_data["#Scan#"][i]
        scan_to_library_map[scan] = {"Compound_Name" : library_search_data["Compound_Name"][i], "SpectrumID" : library_search_data["SpectrumID"][i]}

    for dataset in all_matches:
        #For each dataset, lets try to find the clustering information
        if len(all_matches[dataset]["matches"]) == 0:
            continue

        most_recent_molecular_networking_job = ming_gnps_library.get_most_recent_continuous_networking_of_dataset(dataset_dict[dataset]["task"])
        molecular_network = get_molecular_network_obj(most_recent_molecular_networking_job)

        for match in all_matches[dataset]["matches"]:
            output_map['specs_filename'].append("specs_ms.mgf")
            output_map['specs_scan'].append(match.query_scan)
            output_map['dataset_id'].append(dataset_dict[dataset]["dataset"])
            output_map['dataset_title'].append(dataset_dict[dataset]["title"])
            output_map['dataset_filename'].append(match.filename)
            output_map['dataset_scan'].append(match.scan)
            output_map['score'].append(match.score)

            #List the library identifications
            if str(match.query_scan) in scan_to_library_map:
                output_map['Compound_Name'].append(scan_to_library_map[str(match.query_scan)]["Compound_Name"])
                output_map['SpectrumID'].append(scan_to_library_map[str(match.query_scan)]["SpectrumID"])
            else:
                output_map['Compound_Name'].append("")
                output_map['SpectrumID'].append("")

            #Lets find all the analogs available
            if molecular_network != None:
                neighbors_in_dataset = molecular_network.get_node_neighbors(match.scan)
                output_map['dataset_neighbors'].append(len(neighbors_in_dataset))
            else:
                output_map['dataset_neighbors'].append(0)



    ming_fileio_library.write_dictionary_table_data(output_map, output_matches_filename)


def get_molecular_network_obj(job_obj):
    try:
        print(job_obj)
        path_to_clusterinfosummary = ming_proteosafe_library.get_proteosafe_result_file_path(job_obj["task"], "continuous", "clusterinfosummarygroup_attributes_withIDs")[0]
        path_to_pairs = ming_proteosafe_library.get_proteosafe_result_file_path(job_obj["task"], "continuous", "networkedges_selfloop")[0]

        molecular_network = molecular_network_library.MolecularNetwork()
        molecular_network.load_network(path_to_clusterinfosummary, path_to_pairs)
        return molecular_network
    except KeyboardInterrupt:
        raise
    except:
        #raise
        return None


if __name__ == "__main__":
    main()

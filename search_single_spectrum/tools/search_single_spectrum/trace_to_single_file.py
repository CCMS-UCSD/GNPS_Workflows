#!/usr/bin/python


import sys
import getopt
import os
import json
import requests
import ming_fileio_library
import ming_gnps_library
import ming_proteosafe_library

def get_metadata_information_per_filename(filename):
    """replacing spectrum with ccms_peak"""
    filename = filename.replace("/spectrum/", "/ccms_peak/")

    url = "https://redu.ucsd.edu/filename?query=%s" % (filename)
    r = requests.get(url, timeout=30)

    return r.json()

#Returns True if up, False if Down
def test_metadata_server():
    try:
        url = "https://redu.ucsd.edu/heartbeat"
        requests.get(url, timeout=30)
    except:
        return False

    return True

def trace_filename(all_datasets, dataset_accession, dataset_scan):
    output_list = []
    for dataset_object in all_datasets:
        if dataset_object["dataset"] == dataset_accession:
            networking_job = ming_gnps_library.get_most_recent_continuous_networking_of_dataset(dataset_object["task"])
            if networking_job == None:
                continue

            url = "https://gnps.ucsd.edu/ProteoSAFe/result_json.jsp?task=%s&view=view_raw_spectra" % (networking_job["task"])
            print(url)
            clustering_membership_list = requests.get(url).json()["blockData"]

            acceptable_raw_spectra = [spectrum for spectrum in clustering_membership_list if spectrum["cluster index"] == dataset_scan]
            print(len(acceptable_raw_spectra))
            unique_files = list(set([spectrum["Original_Path"] for spectrum in acceptable_raw_spectra]))
            print(len(unique_files))
            for source_file in unique_files:
                output_object = {}
                output_object["dataset_id"] = dataset_accession
                output_object["dataset_scan"] = dataset_scan
                output_object["filename"] = source_file

                output_list.append(output_object)

    return output_list

def trace_filename_filesystem(all_datasets, dataset_accession, dataset_scan, enrichmetadata=False):
    output_file_list = []
    output_match_list = []
    for dataset_object in all_datasets:
        if dataset_object["dataset"] == dataset_accession:
            networking_job = ming_gnps_library.get_most_recent_continuous_networking_of_dataset(dataset_object["task"])
            if networking_job == None:
                continue

            networking_task_info = ming_proteosafe_library.get_task_information("gnps.ucsd.edu", networking_job["task"])
            task_user = networking_task_info["user"]

            clustering_path = os.path.join("/data/ccms-data/tasks", task_user, networking_job["task"], "allclustered_spectra_info_withpath")
            clustering_files = ming_fileio_library.list_files_in_dir(clustering_path)
            if len(clustering_files) != 1:
                continue

            clustering_membership_list = ming_fileio_library.parse_table_with_headers_object_list(clustering_files[0])

            acceptable_raw_spectra = [spectrum for spectrum in clustering_membership_list if spectrum["cluster index"] == str(dataset_scan)]

            for raw_spectrum in acceptable_raw_spectra:
                output_object = {}
                output_object["dataset_id"] = dataset_accession
                output_object["cluster_scan"] = dataset_scan
                output_object["filename"] = raw_spectrum["Original_Path"]
                output_object["filescan"] = raw_spectrum["ScanNumber"]
                output_object["metadata"] = ""

                if enrichmetadata:
                    try:
                        metadata_list = get_metadata_information_per_filename(raw_spectrum["Original_Path"])
                        output_object["metadata"] = "|".join(metadata_list)
                    except:
                        print("ReDU is down")

                output_match_list.append(output_object)

            print(len(acceptable_raw_spectra))
            unique_files = list(set([spectrum["Original_Path"] for spectrum in acceptable_raw_spectra]))
            print(len(unique_files))
            for source_file in unique_files:
                output_object = {}
                output_object["dataset_id"] = dataset_accession
                output_object["cluster_scan"] = dataset_scan
                output_object["filename"] = source_file
                output_object["metadata"] = ""

                if enrichmetadata:
                    try:
                        metadata_list = get_metadata_information_per_filename(source_file)
                        output_object["metadata"] = "|".join(metadata_list)
                    except:
                        print("ReDU is down")

                output_file_list.append(output_object)

    #Performing a fix to make sure the spectrum is present because of a renaming from <dataset>/spectrum to <dataset>/ccms_peak
    for file_dict in output_file_list:
        splits = file_dict["filename"].split("/")
        splits[1] = splits[1].replace("spectrum", "ccms_peak")
        file_dict["filename"] = "/".join(splits)

    for file_dict in output_match_list:
        splits = file_dict["filename"].split("/")
        splits[1] = splits[1].replace("spectrum", "ccms_peak")
        file_dict["filename"] = "/".join(splits)

    return output_file_list, output_match_list

def main():
    results_filename = sys.argv[1]
    output_filename_unique_files = sys.argv[2]
    output_filename_all_matches = sys.argv[3]

    all_datasets = ming_gnps_library.get_all_datasets(gnps_only=True)
    all_matches = ming_fileio_library.parse_table_with_headers_object_list(results_filename)

    output_source_list = []
    output_match_list = []

    MetaDataServerStatus = test_metadata_server()

    for match_object in all_matches:
        dataset_accession = match_object["dataset_id"]
        dataset_scan = match_object["dataset_scan"]

        #output_source_list += trace_filename(all_datasets, dataset_accession, dataset_scan)
        current_filelist, current_match_list = trace_filename_filesystem(all_datasets, dataset_accession, dataset_scan, enrichmetadata=MetaDataServerStatus)
        output_source_list += current_filelist
        output_match_list += current_match_list

    ming_fileio_library.write_list_dict_table_data(output_source_list, output_filename_unique_files)
    ming_fileio_library.write_list_dict_table_data(output_match_list, output_filename_all_matches)


if __name__ == "__main__":
    main()

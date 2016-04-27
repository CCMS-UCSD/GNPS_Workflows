#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import ming_fileio_library
import molecular_network_library

def usage():
    print "<input clusterinfo file> <param xml> <input usable cluster info summary file> <output file>"


def create_bucket_from_clusterinfo(cluster_info_filename, param_filename, clusterinfosummary_filename, output_filename):
    param_object = ming_proteosafe_library.parse_xml_file(open(param_filename, "r"))
    output_file = open(output_filename, "w")
    if param_object["CREATE_CLUSTER_BUCKETS"][0] != "1":
        output_file.write("No Output")
        return


    test_network = molecular_network_library.MolecularNetwork()
    test_network.load_clustersummary(clusterinfosummary_filename)


    line_counts, table_data = ming_fileio_library.parse_table_with_headers(cluster_info_filename)


    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(param_object)

    cluster_index_to_file_map = {}

    clusters_map = {}
    all_files = {}
    for i in range(line_counts):
        cluster_number = table_data["#ClusterIdx"][i]
        if test_network.get_cluster_index(cluster_number) == None:
            continue

        if not (cluster_number in clusters_map):
            clusters_map[cluster_number] = []
            cluster_index_to_file_map[cluster_number] = {}
            #Adding all file names to mapping
            for mangled_name in mangled_mapping.keys():
                cluster_index_to_file_map[cluster_number][mangled_name] = 0.0

        #print table_data["#Filename"][i].split("/")[1]
        mangled_filename_only = os.path.basename(table_data["#Filename"][i])
        cluster_index_to_file_map[cluster_number][mangled_filename_only] += float(table_data["#PrecIntensity"][i])
        spectrum_info = {"filename":table_data["#Filename"][i], "intensity": table_data["#PrecIntensity"][i]}
        all_files[table_data["#Filename"][i]] = 1
        clusters_map[cluster_number].append(spectrum_info)

    output_header = "#OTU ID\t"
    for header in mangled_mapping.keys():
        output_header += os.path.basename(mangled_mapping[header]) + "\t"

    output_file.write(output_header + "\n")

    for cluster_idx in cluster_index_to_file_map:
        line_string = str(cluster_idx) + "\t"
        for header in mangled_mapping.keys():
            line_string += str(cluster_index_to_file_map[cluster_idx][header]) + "\t"

        #print line_string
        output_file.write(line_string + "\n")

def main():
    input_clusterinfo_file = sys.argv[1]
    param_filename = sys.argv[2]
    input_clusterinfosummary = sys.argv[3]
    output_filename = sys.argv[4]

    create_bucket_from_clusterinfo(input_clusterinfo_file, param_filename, input_clusterinfosummary, output_filename)

if __name__ == "__main__":
    main()

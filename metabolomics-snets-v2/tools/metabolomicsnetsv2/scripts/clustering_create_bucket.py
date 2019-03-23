#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import ming_fileio_library
import argparse
import csv

csv.field_size_limit(sys.maxsize)

def create_bucket_from_clusterinfo(cluster_info_filename, param_filename, clusterinfosummary_filename, output_filename, metadata_mapping):
    output_file = open(output_filename, "w")
    line_counts, table_data = ming_fileio_library.parse_table_with_headers(cluster_info_filename)
    param_object = ming_proteosafe_library.parse_xml_file(open(param_filename, "r"))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(param_object)


    clusters_in_network = set()
    for row in csv.DictReader(open(clusterinfosummary_filename), delimiter='\t'):
        clusters_in_network.add(row["cluster index"])

    cluster_index_to_file_map = {}

    clusters_map = {}
    all_files = {}
    for i in range(line_counts):
        cluster_number = table_data["#ClusterIdx"][i]
        if not(cluster_number in clusters_in_network):
            continue

        if not (cluster_number in clusters_map):
            clusters_map[cluster_number] = []
            cluster_index_to_file_map[cluster_number] = {}
            #Adding all file names to mapping
            for mangled_name in mangled_mapping.keys():
                cluster_index_to_file_map[cluster_number][mangled_name] = 0.0

        #print table_data["#Filename"][i].split("/")[1]
        mangled_filename_only = os.path.basename(table_data["#Filename"][i])
        cluster_index_to_file_map[cluster_number][mangled_filename_only] += max(float(table_data["#PrecIntensity"][i]), 1.0)
        spectrum_info = {"filename":table_data["#Filename"][i], "intensity": table_data["#PrecIntensity"][i]}
        all_files[table_data["#Filename"][i]] = 1
        clusters_map[cluster_number].append(spectrum_info)

    output_header_list = []
    output_header_list.append("#OTU ID")
    for header in mangled_mapping.keys():
        if header.find("spec") == -1:
            continue
        if os.path.basename(mangled_mapping[header]) in metadata_mapping:
            output_header_list.append(metadata_mapping[os.path.basename(mangled_mapping[header])])
        else:
            output_header_list.append(ming_fileio_library.get_filename_without_extension(os.path.basename(mangled_mapping[header])))

    output_file.write("\t".join(output_header_list) + "\n")

    for cluster_idx in cluster_index_to_file_map:
        line_output_list = []
        line_output_list.append(str(cluster_idx))
        #line_string = str(cluster_idx) + "\t"
        for header in mangled_mapping.keys():
            if header.find("spec") == -1:
                continue
            line_output_list.append(str(cluster_index_to_file_map[cluster_idx][header]))
            #line_string += str(cluster_index_to_file_map[cluster_idx][header]) + "\t"

        #print line_string
        #output_file.write(line_string + "\n")
        output_file.write("\t".join(line_output_list) + "\n")
    output_file.close()

def main():
    parser = argparse.ArgumentParser(description='Creates bucket table')
    parser.add_argument('input_clusterinfo_file', help='input_clusterinfo_file')
    parser.add_argument('CREATE_CLUSTER_BUCKETS', help='CREATE_CLUSTER_BUCKETS')
    parser.add_argument('param_filename', help='param_filename')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('output_filename', help='output_filename')
    args = parser.parse_args()


    input_clusterinfo_file = args.input_clusterinfo_file
    param_filename = args.param_filename
    input_clusterinfosummary = args.input_clusterinfosummary
    output_filename = args.output_filename

    metadata_mapping = {}

    if args.CREATE_CLUSTER_BUCKETS == "1":
        create_bucket_from_clusterinfo(input_clusterinfo_file, param_filename, input_clusterinfosummary, output_filename, metadata_mapping)
    else:
        open(output_filename, "w").write("No Output")


if __name__ == "__main__":
    main()

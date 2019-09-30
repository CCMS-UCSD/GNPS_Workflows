#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import ming_fileio_library
import argparse
import csv

csv.field_size_limit(sys.maxsize)


def usage():
    print("<input clusterinfo file> <param xml> <input usable cluster info summary file> <output file> <output biom filename> <path to python runtime> <path to biom script>")


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

def create_biom_file(input_tsv_filename, output_biom_filename, python_runtime, biom_run_script):
    command = "%s %s convert -i %s -o %s --to-hdf5 --table-type=\"OTU table\"" % (python_runtime, biom_run_script, input_tsv_filename, output_biom_filename)
    os.system(command)

    if not os.path.isfile(output_biom_filename):
        open(output_biom_filename, "w").write("Error BioM Conversion")


def load_metadata_mapping(metadata_folder):
    file_name_to_sample_id_mapping = {}
    all_files = ming_fileio_library.list_files_in_dir(metadata_folder)

    if len(all_files) != 1:
        return {}

    row_count, table_data = ming_fileio_library.parse_table_with_headers(all_files[0])

    for i in range(row_count):
        filename = table_data["filename"][i]
        sample_id = table_data["#SampleID"][i]

        file_name_to_sample_id_mapping[filename] = sample_id

    return file_name_to_sample_id_mapping

def main():
    parser = argparse.ArgumentParser(description='Creates bucket table')
    parser.add_argument('input_clusterinfo_file', help='input_clusterinfo_file')
    parser.add_argument('param_filename', help='param_filename')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('output_filename', help='output_filename')
    parser.add_argument('output_biom_filename', help='output_biom_filename')
    parser.add_argument('python_runtime', help='python_runtime')
    parser.add_argument('biom_run_script', help='biom_run_script')
    parser.add_argument('--metadata_folder', help='Metadata folder')
    args = parser.parse_args()

    # input_clusterinfo_file = sys.argv[1]
    # param_filename = sys.argv[2]
    # input_clusterinfosummary = sys.argv[3]
    # output_filename = sys.argv[4]
    # output_biom_filename = sys.argv[5]
    # python_runtime = sys.argv[6]
    # biom_run_script = sys.argv[7]

    input_clusterinfo_file = args.input_clusterinfo_file
    param_filename = args.param_filename
    input_clusterinfosummary = args.input_clusterinfosummary
    output_filename = args.output_filename
    output_biom_filename = args.output_biom_filename
    python_runtime = args.python_runtime
    biom_run_script = args.biom_run_script

    metadata_mapping = {}
    try:
        metadata_mapping = load_metadata_mapping(args.metadata_folder)
    except:
        metadata_mapping = {}

    create_buckets = True
    param_object = ming_proteosafe_library.parse_xml_file(open(param_filename, "r"))
    try:
        if param_object["CREATE_CLUSTER_BUCKETS"][0] != "1":
            create_buckets = False
    except:
        create_buckets = False

    if create_buckets:
        create_bucket_from_clusterinfo(input_clusterinfo_file, param_filename, input_clusterinfosummary, output_filename, metadata_mapping)
        create_biom_file(output_filename, output_biom_filename, python_runtime, biom_run_script)
    else:
        open(output_filename, "w").write("No Output")
        open(output_biom_filename, "w").write("No Output")


if __name__ == "__main__":
    main()

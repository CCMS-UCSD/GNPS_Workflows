#!/usr/bin/python


import sys
import getopt
import os
import ming_proteosafe_library
import ming_fileio_library
import molecular_network_library
import argparse
import statistics

from collections import defaultdict

def load_group_mapping(filename):
    default_groups = ['G1','G2','G3','G4','G5','G6']
    group_to_files = defaultdict(list)
    files_to_groups = defaultdict(list)

    for line in open(filename):
        splits = line.split("=")
        if len(splits) != 2:
            continue
        group_name = splits[0].replace("GROUP_", "")
        files_path = splits[1].rstrip().split(";")

        if group_name in default_groups:
            group_name = group_name
        else:
            group_name = "GNPSGROUP:" + group_name

        for filename in files_path:
            file_basename = os.path.basename(filename)
            group_to_files[group_name].append(file_basename)
            files_to_groups[file_basename].append(group_name)

    return group_to_files, files_to_groups

def load_attribute_mapping(filename):
    attribute_to_groups = {}
    for line in open(filename):
        attribute_name = "ATTRIBUTE_" + line.split("=")[0]
        group_list = line.split("=")[1].rstrip().split(";")
        group_list = [("GNPSGROUP:" + group_name) for group_name in group_list]

        attribute_to_groups[attribute_name] = group_list

    return attribute_to_groups

#Adding more columns
def calculate_default_attributes(all_clusters_list, group_names):
    default_groups = ['G1','G2','G3','G4','G5','G6']
    for cluster in all_clusters_list:
        default_groups_in_cluster = []
        for default_group in default_groups:
            if cluster[default_group] > 0:
                default_groups_in_cluster.append(default_group)

        cluster["DefaultGroups"] = ",".join(default_groups_in_cluster)

        other_groups_in_cluster = []
        for group_name in group_names:
            if group_name in default_groups:
                continue

            if cluster[group_name] > 0:
                other_groups_in_cluster.append(group_name)

        cluster["AllGroups"] = ",".join(other_groups_in_cluster).replace("GNPSGROUP:", "")

def calculate_cluster_file_stats(all_clusters_list, clusters_to_files, mangled_mapping):
    for cluster in all_clusters_list:
        all_files_per_cluster = [os.path.basename(mangled_mapping[mangled_name]) for mangled_name in clusters_to_files[cluster["cluster index"]]]
        cluster["UniqueFileSourcesCount"] = len(all_files_per_cluster)
        cluster["UniqueFileSources"] = "|".join(all_files_per_cluster)

def calculate_rt_stats(cluster_summary_list, cluster_to_RT):
    for cluster in cluster_summary_list:
        try:
            cluster["RTMean"] = statistics.mean(cluster_to_RT[cluster["cluster index"]])
            cluster["RTStdErr"] = statistics.pstdev(cluster_to_RT[cluster["cluster index"]])
        except:
            cluster["RTMean"] = 0
            cluster["RTStdErr"] = 0

def calculate_ancillary_information(all_clusters_list, task):
    for cluster in all_clusters_list:
        cluster_membership_url = "https://gnps.ucsd.edu//ProteoSAFe/result.jsp?task=%s&view=cluster_details&protein=%s&show=true" % (task, cluster["cluster index"])
        cluster["GNPSLinkout_Cluster"] = cluster_membership_url
        cluster["GNPSLinkout_Network"] = "https://gnps.ucsd.edu/ProteoSAFe/result.jsp?view=network_displayer&componentindex=%s&task=%s&show=true" % (cluster["componentindex"], task)
        
        charge = int(cluster["precursor charge"])
        precursor = float(cluster["parent mass"])
        if charge == 0:
            charge = 1
        even_odd_number = precursor - charge
        even_odd_number = even_odd_number * 0.9995
        even_odd_value = int(even_odd_number) % 2

        cluster["EvenOdd"] = even_odd_value

def filter_clusters_based_on_cluster_size(all_clusters_list, minimum_cluster_size):
    new_cluster_list = []
    for cluster in all_clusters_list:
        if int(cluster["number of spectra"]) < minimum_cluster_size:
            continue
        new_cluster_list.append(cluster)

    return new_cluster_list


def populate_network_component(all_clusters_list, pairs_filename):
    cluster_to_component = defaultdict(lambda: -1)
    for line in open(pairs_filename):
        splits = line.rstrip().split("\t")
        node1 = splits[0]
        node2 = splits[1]
        component = splits[-1]
        cluster_to_component[node1] = component
        cluster_to_component[node2] = component

    for cluster in all_clusters_list:
        cluster_index = cluster["cluster index"]
        cluster["componentindex"] = cluster_to_component[cluster_index]

def populate_network_identifications(cluster_summary_list, library_search_filename):
    clusters_to_identifications = {}
    library_ids_list = ming_fileio_library.parse_table_with_headers_object_list(library_search_filename)
    for library_id in library_ids_list:
        cluster_index = library_id["#Scan#"]
        clusters_to_identifications[cluster_index] = library_id

    fields_to_copy = ["Smiles", "MQScore", "MassDiff", "MZErrorPPM", "SpectrumID", "Smiles"]
    for cluster in cluster_summary_list:
        cluster_index = cluster["cluster index"]
        if cluster_index in clusters_to_identifications:
            cluster["LibraryID"] = clusters_to_identifications[cluster_index]["Compound_Name"]
            for field in fields_to_copy:
                cluster[field] = clusters_to_identifications[cluster_index][field]
        else:
            cluster["LibraryID"] = "N/A"
            for field in fields_to_copy:
                cluster[field] = "N/A"





def main():
    parser = argparse.ArgumentParser(description='Creates enriched cluster info summary')
    parser.add_argument('param_xml', help='param_xml')
    parser.add_argument('input_clusterinfo_file', help='input_clusterinfo_file')
    parser.add_argument('input_clusterinfosummary_file', help='input_clusterinfosummary_file')
    parser.add_argument('input_group_mapping_filename', help='input_group_mapping_filename')
    parser.add_argument('input_attribute_mapping_filename', help='input_attribute_mapping_filename')
    parser.add_argument('input_networking_pairs', help='input_networking_pairs')
    parser.add_argument('input_library_search', help='input_library_search')
    parser.add_argument('output_clusterinfosummary_filename', help='output_clusterinfosummary_filename')
    args = parser.parse_args()

    """Loading group filenames"""
    group_to_files, files_to_groups = load_group_mapping(args.input_group_mapping_filename)
    print("Loaded Group Mapping")
    cluster_summary_list = ming_fileio_library.parse_table_with_headers_object_list(args.input_clusterinfosummary_file)
    print("Loaded Cluster Summary")

    attribute_to_groups = load_attribute_mapping(args.input_attribute_mapping_filename)

    params_object = ming_proteosafe_library.parse_xml_file(open(args.param_xml))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_object)

    CLUSTER_MIN_SIZE = int(params_object["CLUSTER_MIN_SIZE"][0])
    RUN_MSCLUSTER = params_object["RUN_MSCLUSTER"][0]

    #Calculating the spectrum counts per group
    cluster_to_group_counts = defaultdict(lambda: defaultdict(lambda: 0))
    cluster_to_files = defaultdict(set)
    cluster_to_RT = defaultdict(list)
    line_count = 0
    for line in open(args.input_clusterinfo_file):
        line_count += 1
        if line_count == 1:
            continue
        if line_count % 10000 == 0:
            print(line_count)

        splits = line.rstrip().split("\t")
        cluster_index = splits[0]
        filename = os.path.basename(splits[1])
        rt = float(splits[6])

        group_membership = files_to_groups[filename]
        cluster_to_files[cluster_index].add(filename)
        cluster_to_RT[cluster_index].append(rt)

        for group in group_membership:
            cluster_to_group_counts[cluster_index][group] += 1

    if RUN_MSCLUSTER == "on":
        cluster_summary_list = filter_clusters_based_on_cluster_size(cluster_summary_list, CLUSTER_MIN_SIZE)

    print(len(cluster_summary_list))

    print("Setting up grouping", len(group_to_files.keys()))
    for cluster_summary_object in cluster_summary_list:
        cluster_index = cluster_summary_object["cluster index"]
        for group in group_to_files:
            group_count = 0
            if group in cluster_to_group_counts[cluster_index]:
                group_count = cluster_to_group_counts[cluster_index][group]
            cluster_summary_object[group] = group_count

        for attribute in attribute_to_groups:
            groups_to_include = []
            for group in attribute_to_groups[attribute]:
                if group in cluster_summary_object:
                    if cluster_summary_object[group] > 0:
                        groups_to_include.append(group)

            cluster_summary_object[attribute] = ",".join(groups_to_include).replace("GNPSGROUP:", "")


    print("Default Attributes")
    calculate_default_attributes(cluster_summary_list, group_to_files.keys())

    print("calculate_cluster_file_stats")
    calculate_cluster_file_stats(cluster_summary_list, cluster_to_files, mangled_mapping)

    print("rt stats")
    calculate_rt_stats(cluster_summary_list, cluster_to_RT)

    print("populate_network_component")
    populate_network_component(cluster_summary_list, args.input_networking_pairs)

    print("calculate_ancillary_information")
    calculate_ancillary_information(cluster_summary_list, params_object["task"][0])    

    print("populate_network_identifications")
    populate_network_identifications(cluster_summary_list, args.input_library_search)

    ming_fileio_library.write_list_dict_table_data(cluster_summary_list, args.output_clusterinfosummary_filename)











if __name__ == "__main__":
    main()

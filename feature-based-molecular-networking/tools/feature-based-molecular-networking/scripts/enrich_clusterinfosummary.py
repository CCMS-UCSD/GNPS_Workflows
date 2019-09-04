#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import ming_fileio_library
import ming_proteosafe_library
from collections import defaultdict

def load_library_id_dict(library_filename):
    results_list = ming_fileio_library.parse_table_with_headers_object_list(library_filename)

    output_dict = {}
    for result_obj in results_list:
        scan = result_obj["#Scan#"]
        output_dict[scan] = result_obj

    return output_dict

""" Creates a dictionary of nodes to component identifiers, and a dictionary of component to nodes
"""
def load_pairs_dict(pairs_filename):
    results_list = ming_fileio_library.parse_table_with_headers_object_list(pairs_filename)

    node_to_component = {}
    component_to_node = defaultdict(set)

    for result_obj in results_list:
        node1 = result_obj["CLUSTERID1"]
        node2 = result_obj["CLUSTERID2"]
        component = result_obj["ComponentIndex"]

        node_to_component[node1] = component
        node_to_component[node2] = component

        component_to_node[component].add(node1)
        component_to_node[component].add(node2)

    return node_to_component, component_to_node


def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('params_xml', help='params_xml')
    parser.add_argument('input_clusterinfo_summary', help='Input cluster info summary')
    parser.add_argument('input_network_pairs_file', help='network_pairs_file')
    parser.add_argument('input_library_search_file', help='network_pairs_file')
    parser.add_argument('output_clusterinfo_summary', help='output file')
    parser.add_argument('output_component_summary', help='output component file')
    args = parser.parse_args()

    param_obj = ming_proteosafe_library.parse_xml_file(open(args.params_xml))

    all_clusterinfo_list = ming_fileio_library.parse_table_with_headers_object_list(args.input_clusterinfo_summary)

    library_ids_dict = load_library_id_dict(args.input_library_search_file)
    nodes_to_component, component_to_nodes = load_pairs_dict(args.input_network_pairs_file)

    for cluster in all_clusterinfo_list:
        cluster_index = cluster["cluster index"]
        if cluster_index in nodes_to_component:
            cluster["componentindex"] = nodes_to_component[cluster_index]
            cluster["GNPSLinkout_Network"] = "https://gnps.ucsd.edu/ProteoSAFe/result.jsp?view=network_displayer&componentindex=%s&task=%s&show=true" % (nodes_to_component[cluster_index], param_obj["task"][0])
        else:
            cluster["componentindex"] = "-1"
            cluster["GNPSLinkout_Network"] = 'This Node is a Singleton'

        if cluster_index in library_ids_dict:
            cluster["LibraryID"] = library_ids_dict[cluster_index]["Compound_Name"]
            cluster["MQScore"] = library_ids_dict[cluster_index]["MQScore"]
            cluster["SpectrumID"] = library_ids_dict[cluster_index]["SpectrumID"]
        else:
            cluster["LibraryID"] = "N/A"
            cluster["MQScore"] = "N/A"
            cluster["SpectrumID"] = "N/A"

    ming_fileio_library.write_list_dict_table_data(all_clusterinfo_list, args.output_clusterinfo_summary)

    output_component_list = []

    for componentindex in component_to_nodes:
        output_dict = {}
        output_dict["ComponentIndex"] = componentindex
        output_dict["NodeCount"] = len(component_to_nodes[componentindex])
        output_dict["#Spectra"] = len(component_to_nodes[componentindex])
        all_lib_identifications = []
        for node in component_to_nodes[componentindex]:
            if node in library_ids_dict:
                all_lib_identifications.append(library_ids_dict[node]["Compound_Name"])
        output_dict["AllIDs"] = "!".join(all_lib_identifications)
        output_component_list.append(output_dict)

    ming_fileio_library.write_list_dict_table_data(output_component_list, args.output_component_summary)








if __name__ == "__main__":
    main()

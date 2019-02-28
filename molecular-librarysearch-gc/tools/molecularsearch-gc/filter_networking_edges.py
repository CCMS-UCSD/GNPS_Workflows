#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import ming_proteosafe_library
import molecular_network_filtering_library
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Creating Clustering Info Summary')
    parser.add_argument('proteosafe_parameters', help='proteosafe_parameters')
    parser.add_argument('networking_pairs_results_file', help='networking_pairs_results_file')
    parser.add_argument('networking_pairs_results_file_filtered', help='networking_pairs_results_file_filtered')
    parser.add_argument('networking_pairs_results_file_filtered_classic_output', help='networking_pairs_results_file_filtered_classic_output')
    args = parser.parse_args()

    param_obj = ming_proteosafe_library.parse_xml_file(open(args.proteosafe_parameters))

    top_k_val = 10
    max_component_size = 0

    if "TOPK" in param_obj:
        top_k_val = int(param_obj["TOPK"][0])

    if "MAXIMUM_COMPONENT_SIZE" in param_obj:
        max_component_size = int(param_obj["MAXIMUM_COMPONENT_SIZE"][0])

    G = molecular_network_filtering_library.loading_network(args.networking_pairs_results_file, hasHeaders=True)
    if G == None:
        exit(0)

    molecular_network_filtering_library.filter_top_k(G, top_k_val)
    molecular_network_filtering_library.filter_component(G, max_component_size)
    molecular_network_filtering_library.output_graph_with_headers(G, args.networking_pairs_results_file_filtered)

    molecular_network_filtering_library.output_graph(G, args.networking_pairs_results_file_filtered_classic_output)


if __name__ == "__main__":
    main()

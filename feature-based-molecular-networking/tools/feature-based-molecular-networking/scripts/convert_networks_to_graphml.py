#!/usr/bin/python


import sys
import getopt
import os
import molecular_network_filtering_library
import ion_network_utils
import glob
import networkx as nx
import argparse


def main():
    parser = argparse.ArgumentParser(description='Creating GraphML')
    parser.add_argument('input_pairs', help='input_pairs')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('input_librarysearch', help='input_librarysearch')
    parser.add_argument('output_graphml', help='output_graphml')
    parser.add_argument('--input_analoglibrarysearch', help='input_analoglibrarysearch')
    # options for ion identity molecular networking:
    # add "neutral molecule" nodes and collapse IIN edges
    # IIN edges = supplemental pairs (input_pairsfolder)
    parser.add_argument('--input_pairsfolder', help='input_pairsfolder')
    parser.add_argument('--collapse_additional_edges', default="False", help='collapse_additional_edges True or False')
    args = parser.parse_args()

    # export graphml to file
    create_graphml(args.input_pairs, args.input_clusterinfosummary, args.input_librarysearch,
                   args.input_analoglibrarysearch, args.input_pairsfolder, args.output_graphml,
                   args.collapse_additional_edges)

    
def create_graphml(input_pairs, input_clusterinfosummary, input_librarysearch, input_analoglibrarysearch,
                   input_pairsfolder, output_graphml, collapse_additional_edges=False):
    # Doing other filtering
    G = molecular_network_filtering_library.loading_network(input_pairs, hasHeaders=True)
    molecular_network_filtering_library.add_clusterinfo_summary_to_graph(G, input_clusterinfosummary)
    molecular_network_filtering_library.add_library_search_results_to_graph(G, input_librarysearch)
    # mark all nodes as feature or ion identity nodes (ion_network_utils.NODE_TYPE_ATTRIBUTE)
    ion_network_utils.mark_all_node_types(G)

    # add analogs
    if input_analoglibrarysearch is not None:
        molecular_network_filtering_library.add_library_search_results_to_graph(G, input_analoglibrarysearch, annotation_prefix="Analog:")

    # add additional edges - e.g. ion identity edges between different ion species of the same molecule
    if input_pairsfolder is not None:
        all_pairs_files = glob.glob(os.path.join(input_pairsfolder, "*"))
        for additional_pairs_file in all_pairs_files:
            print("Adding Additional Edges", additional_pairs_file)
            molecular_network_filtering_library.add_additional_edges(G, additional_pairs_file)

        # collapse all ion identity networks, each into a single node
        if collapse_additional_edges:
            G = ion_network_utils.collapse_ion_networks(G)

    # export graphml
    nx.write_graphml(G, output_graphml, infer_numeric_types=True)

if __name__ == "__main__":
    main()

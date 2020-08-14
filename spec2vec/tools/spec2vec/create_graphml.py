#!/usr/bin/python

import sys
import getopt
import os
import molecular_network_filtering_library
import argparse
import networkx as nx
import glob

def main():
    parser = argparse.ArgumentParser(description='Processing Graphml for Spec2Vec')
    parser.add_argument('input_pairs_file', help='input_pairs_file')
    parser.add_argument('input_graphml_folder', help='input_graphml_folder')
    parser.add_argument('output_folder', help='output_folder')
    args = parser.parse_args()

    top_k_val = 10
    max_component_size = 10

    # Loading Network if it exists
    try:
        G = nx.read_graphml(glob.glob(os.path.join(args.input_graphml_folder, "*"))[0])
        # Let's do some pruning of the edges

    except:
        G = molecular_network_filtering_library.loading_network(args.input_pairs_file, hasHeaders=True, edgetype="Spec2Vec")
    
    #Returning None means that there are no edges in the output
    if G == None:
        exit(0)
    molecular_network_filtering_library.filter_top_k(G, top_k_val)
    molecular_network_filtering_library.filter_component(G, max_component_size)

    output_graphml = os.path.join(args.output_folder, "gnps_network.graphml")
    output_pairs = os.path.join(args.output_folder, "filtered_pairs.tsv")
    molecular_network_filtering_library.output_graph(G, output_pairs)

    nx.write_graphml(G, output_graphml)

if __name__ == "__main__":
    main()

#!/usr/bin/python

import sys
import getopt
import os
import molecular_network_filtering_library
import argparse
import networkx as nx
import glob
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Processing Graphml for Spec2Vec')
    parser.add_argument('input_pairs_file', help='input_pairs_file')
    parser.add_argument('input_graphml_folder', help='input_graphml_folder')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument('--topk', default=50, type=int, help='mutual top k')
    parser.add_argument('--removecosine', default="yes", help='remove cosine edges')
    parser.add_argument('--max_component_size', default=100, type=int, help='max component size')
    parser.add_argument('--component_filtering', default="breakup", help='max component size')
    args = parser.parse_args()

    top_k_val = int(args.topk)
    max_component_size = args.max_component_size

    # Trying to load the new spec2vec network
    new_G = molecular_network_filtering_library.loading_network(args.input_pairs_file, hasHeaders=True, edgetype="Spec2Vec")

    #Returning None means that there are no edges in the output
    if new_G == None:
        print("No Edges")
        exit(1)

    # Filtering the spec2vec network
    molecular_network_filtering_library.filter_top_k(new_G, top_k_val)
    if args.component_filtering == "breakup":
        molecular_network_filtering_library.filter_component(new_G, max_component_size)
    elif args.component_filtering == "additive":
        molecular_network_filtering_library.filter_component_additive(new_G, max_component_size)

    # Deteriming if we should combine with cosine network
    try:
        old_G = nx.read_graphml(glob.glob(os.path.join(args.input_graphml_folder, "*"))[0])

        # Let's do some pruning of the edges
        if args.removecosine == "yes":
            old_G.remove_edges_from(list(old_G.edges()))

        old_G = nx.MultiGraph(old_G)
        new_G = nx.MultiGraph(new_G)

        G = nx.compose(old_G, new_G)
    except:
        G = new_G
    
    output_graphml = os.path.join(args.output_folder, "gnps_spec2vec.graphml")
    output_pairs = os.path.join(args.output_folder, "filtered_pairs.tsv")
    molecular_network_filtering_library.output_graph_with_headers(G, output_pairs)

    nx.write_graphml(G, output_graphml)

if __name__ == "__main__":
    main()

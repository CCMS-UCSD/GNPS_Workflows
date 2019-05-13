#!/usr/bin/python


import sys
import getopt
import os
import molecular_network_filtering_library
import ming_fileio_library
import networkx as nx

def main():
    input_pairs = sys.argv[1]

    #Doing other filtering
    G = molecular_network_filtering_library.loading_network(input_pairs, hasHeaders=True)
    molecular_network_filtering_library.add_clusterinfo_summary_to_graph(G, sys.argv[2])
    molecular_network_filtering_library.add_library_search_results_to_graph(G, sys.argv[3])

    folder_for_additional_pairs = sys.argv[4]
    all_pairs_files = ming_fileio_library.list_files_in_dir(folder_for_additional_pairs)
    for additional_pairs_file in all_pairs_files:
        print("Adding Additional Edges", additional_pairs_file)
        molecular_network_filtering_library.add_additional_edges(G, additional_pairs_file)


    nx.write_graphml(G, sys.argv[5], infer_numeric_types=True)



if __name__ == "__main__":
    main()

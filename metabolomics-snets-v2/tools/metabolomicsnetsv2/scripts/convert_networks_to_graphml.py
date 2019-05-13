#!/usr/bin/python


import sys
import getopt
import os
import molecular_network_filtering_library
import networkx as nx

def usage():
    print("<pairs info> <cluster info summary> <library identifications> <output graphml filename>")


def main():
    input_pairs = sys.argv[1]

    #Doing other filtering
    G = molecular_network_filtering_library.loading_network(input_pairs, hasHeaders=True)
    molecular_network_filtering_library.add_clusterinfo_summary_to_graph(G, sys.argv[2])
    molecular_network_filtering_library.add_library_search_results_to_graph(G, sys.argv[3])

    nx.write_graphml(G, sys.argv[4], infer_numeric_types=True)




if __name__ == "__main__":
    main()

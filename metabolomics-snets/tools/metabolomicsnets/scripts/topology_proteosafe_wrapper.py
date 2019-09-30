#!/usr/bin/python


import sys
import getopt
import os
import math
from molecular_network_library import MolecularNetwork, ClusterNode, NetworkPair
import networkx as nx
import ming_fileio_library
import ming_proteosafe_library
import json
import topology_library


def usage():
    print "<param.xml> <input pairs info> <clusterinfo file> <output path list> <output path histogram>"

def find_features_in_network(clusterinfo_filename, pairs_info_filename, output_path_list_filename, output_path_histogram_filename):
    #Creating molecular network
    molecular_network = MolecularNetwork()
    molecular_network.load_network(clusterinfo_filename, pairs_info_filename)

    #get_mzdelta_topology_aware_clusters(molecular_network, [162], 1.0)
    path_list_comprehensive = topology_library.get_all_topology_paths(molecular_network, 3)
    topology_library.output_path_list(path_list_comprehensive, output_path_list_filename)
    topology_library.output_path_list_histogram(path_list_comprehensive, output_path_histogram_filename)

def main():
    paramxml_input_filename = sys.argv[1]
    pairs_info_filename = sys.argv[2]
    clusterinfo_filename = sys.argv[3]
    output_all_paths_filename = sys.argv[4]
    output_all_paths_histogram_filename = sys.argv[5]

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))
    try:
        if params_obj["CREATE_TOPOLOGY_SIGNATURES"][0] != "1":
            open(output_all_paths_filename, "w").write("NONE")
            open(output_all_paths_histogram_filename, "w").write("NONE")
            exit(0)
    except:
        open(output_all_paths_filename, "w").write("NONE")
        open(output_all_paths_histogram_filename, "w").write("NONE")
        exit(0)

    find_features_in_network(clusterinfo_filename, pairs_info_filename, output_all_paths_filename, output_all_paths_histogram_filename)

if __name__ == "__main__":
    main()

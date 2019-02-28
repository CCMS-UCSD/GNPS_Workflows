#!/usr/bin/python


import sys
import getopt
import os
import math
from network_utils import MolecularNetwork, ClusterNode, NetworkPair



def usage():
    print "<input clustersummary with IDs> <input pairsinfo with component index> <output clustersummary> <output components file>"



def main():
    usage()

    #Creating molecular network
    molecular_network = MolecularNetwork("my network")

    molecular_network.load_clusterinfo_summary_file(sys.argv[1])
    molecular_network.load_pairs_file_noheaders(sys.argv[2])

    output_file = open(sys.argv[3], "w")
    output_file.write(molecular_network.clusterinfosummary_file_header + "\t" + "componentindex" + "\n")

    for node_id in molecular_network.cluster_to_nodedata:
        output_file.write(molecular_network.cluster_to_nodedata[node_id].originalstringline + "\t" + str(molecular_network.cluster_to_nodedata[node_id].componentindex) + "\n")

    #Writing connected component file
    output_components_file = open(sys.argv[4], "w")
    output_components_file.write("ComponentIndex\tNodeCount\tAllIDs\t%ID\t#Spectra\tDefaultGroups\tUserGroups\n")
    connected_components = molecular_network.get_all_connected_components()

    for component in connected_components:
        output_components_file.write(str(component.componentindex) + "\t")
        output_components_file.write(str(component.get_number_of_nodes()) + "\t")
        output_components_file.write(str(component.get_component_identifications()) + "\t")
        output_components_file.write(str(component.get_percent_nodes_id()) + "\t")
        output_components_file.write(str(component.get_number_of_spectra()) + "\t")
        output_components_file.write(str(component.get_component_groups_default()) + "\t")
        output_components_file.write(str(component.get_component_groups_user()) + "\n")




if __name__ == "__main__":
    main()

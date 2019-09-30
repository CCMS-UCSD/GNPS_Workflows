#!/usr/bin/python


import sys
import getopt
import os
import math
from network_utils import MolecularNetwork, ClusterNode, NetworkPair
import argparse


def main():
    parser = argparse.ArgumentParser(description='Creates enriched cluster info summary')
    parser.add_argument('input_clustersummary', help='input_clustersummary')
    parser.add_argument('input_pairs', help='input_pairs')
    parser.add_argument('output_components', help='output_components')
    args = parser.parse_args()

    #Creating molecular network
    molecular_network = MolecularNetwork("my network")

    molecular_network.load_clusterinfo_summary_file(args.input_clustersummary)
    molecular_network.load_pairs_file_noheaders(args.input_pairs)

    #Writing connected component file
    output_components_file = open(args.output_components, "w")
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

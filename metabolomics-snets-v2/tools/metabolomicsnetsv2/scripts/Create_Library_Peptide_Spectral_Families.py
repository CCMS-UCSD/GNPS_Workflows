#!/usr/bin/python


import sys
import getopt
import os
import math
from network_utils import MolecularNetwork, ClusterNode, NetworkPair



def usage():
    print "<input clustersummary with IDs> <input pairsinfo with component index> <2 Pass Peptide ID File> <output components file>"
    
    

def main():
    usage()
    
    #Creating molecular network
    molecular_network = MolecularNetwork("my network")
    
    molecular_network.load_clusterinfo_summary_file(sys.argv[1])
    molecular_network.load_pairs_file_noheaders(sys.argv[2])
    molecular_network.load_peptide_identification_2pass(sys.argv[3])
    
    #Writing connected component file
    output_components_file = open(sys.argv[4], "w")
    output_components_file.write("ComponentIndex\tNodeCount\tAllIDs\t%ID\t#Spectra\tAllPeptides\n")
    connected_components = molecular_network.get_all_connected_components()
    
    for component in connected_components:
        output_components_file.write(str(component.componentindex) + "\t")
        output_components_file.write(str(component.get_number_of_nodes()) + "\t")
        output_components_file.write(str(component.get_component_identifications()) + "\t")
        output_components_file.write(str(component.get_percent_nodes_id()) + "\t")
        output_components_file.write(str(component.get_number_of_spectra()) + "\t")
        output_components_file.write(str(component.get_component_peptides()) + "\n")
        
    
    
    
if __name__ == "__main__":
    main()
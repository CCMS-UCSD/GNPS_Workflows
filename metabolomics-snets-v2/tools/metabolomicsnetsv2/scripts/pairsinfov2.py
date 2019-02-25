#!/usr/bin/python


import sys
import getopt
import os
import molecular_network_filtering_library
import ming_proteosafe_library

def usage():
    print("--outfile <output file> --input-file <input file> <flowparams> <path to pairsinfo>")

def main():
    usage()

    output_file_path = sys.argv[2]
    input_file_path = sys.argv[4]
    params_file_path = sys.argv[5]
    top_k_val = 10
    max_component_size = 0

    params = ming_proteosafe_library.parse_xml_file(open(params_file_path, "r"))

    if "TOPK" in params:
        top_k_val = int(params["TOPK"][0])

    if "MAXIMUM_COMPONENT_SIZE" in params:
        max_component_size = int(params["MAXIMUM_COMPONENT_SIZE"][0])

    #Doing other filtering
    G = molecular_network_filtering_library.loading_network(input_file_path, hasHeaders=True)
    #Returning None means that there are no edges in the output
    if G == None:
        exit(0)
    molecular_network_filtering_library.filter_top_k(G, top_k_val)
    molecular_network_filtering_library.filter_component(G, max_component_size)
    molecular_network_filtering_library.output_graph(G, output_file_path)

if __name__ == "__main__":
    main()

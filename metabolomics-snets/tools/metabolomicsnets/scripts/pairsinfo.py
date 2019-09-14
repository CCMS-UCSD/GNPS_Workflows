#!/usr/bin/python


import sys
import getopt
import os

def parse_xml_file(input_file):
    key_value_pairs = {}
    for line in input_file:
        #print line
        new_line = line.rstrip().replace("<parameter name=\"", "")
        #new_line = new_line.replace("\">", "=")
        new_line = new_line.replace("</parameter>", "")
        
        splits = new_line.split("\">")
        #print splits
        if(len(splits) != 2):
            continue
          

        if(splits[0] in key_value_pairs.keys()):
          key_value_pairs[splits[0]].append(splits[1])
        else:
          key_value_pairs[splits[0]] = []
          key_value_pairs[splits[0]].append(splits[1])
        
        
    return key_value_pairs


def usage():
    print "--outfile <output file> --input-file <input file> <flowparams> <path to pairsinfo>"
    

    
    
def main():
    usage()
    
    #mgf_file = open(sys.argv[2], "r")
    output_file_path = sys.argv[2]
    input_file_path = sys.argv[4]
    params_file_path = sys.argv[5]
    pairsinfo_path = sys.argv[6]
    top_k_val = 10
    max_component_size = 0
    
    params = parse_xml_file(open(params_file_path, "r"))
    
    if "TOPK" in params:
        top_k_val = int(params["TOPK"][0])
    
    if "MAXIMUM_COMPONENT_SIZE" in params:
        max_component_size = int(params["MAXIMUM_COMPONENT_SIZE"][0])
    
    full_command = pairsinfo_path + " " + "--outfile " + output_file_path + " --input-file " + input_file_path + " --edge-topk-both " + str(top_k_val)
    
    if max_component_size != 0:
        full_command += " --max-component-size " + str(max_component_size)
    
    print full_command
    os.system(full_command)
    
if __name__ == "__main__":
    main()
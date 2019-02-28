#!/usr/bin/python


import sys
import getopt
import random 
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

def get_mangled_file_mapping(params):
    all_mappings = params["upload_file_mapping"]
    mangled_mapping = {}
    for mapping in all_mappings:
        print mapping
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[mangled_name] = original_name
    
    return mangled_mapping


def usage():
    print "<input params file> <input cluster info> <output cluster info file>"
    

    
    
def main():
    usage()
    
    params_filename = sys.argv[1]
    clusterinfo_input_filename = sys.argv[2]
    clusterinfo_output_filename = sys.argv[3]
    
    params = parse_xml_file(open(params_filename, 'r'))
    manged_mapping = get_mangled_file_mapping(params)
    
    clusterinfo_input = open(clusterinfo_input_filename, 'r')
    clusterinfo_output = open(clusterinfo_output_filename, 'w')
    
    line_count = 0
    for line in clusterinfo_input:
        line_count += 1
        clusterinfo_output.write(line.rstrip())
        
        if(line_count == 1):
            clusterinfo_output.write("\tOriginal_Path\n")
            continue
        
        mangled_task_path = line.split("\t")[7].rstrip()
        mangled_filename = os.path.basename(mangled_task_path)
        #print mangled_filename
        original_filename = manged_mapping[mangled_filename]
        #print original_filename
        clusterinfo_output.write("\tf." + original_filename + "\n")
    

if __name__ == "__main__":
    main()
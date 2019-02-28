#!/usr/bin/python


import sys
import getopt
import os



def usage():
    print "<input network edges> <output results view> <output results pairs view> <path to specs_ms.pklbin>"
    
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
        key_value_pairs[splits[0]] = splits[1]
        
    return key_value_pairs
    
    
def main():
    usage()
    
    input_network_edges_file = open(sys.argv[1], "r")
    output_network_file = open(sys.argv[2], "w")
    output_network_pairs_file = open(sys.argv[3], "w")
    path_to_specs_file = sys.argv[4];

    print "READING Network FILE"
    
    cluster_neighbors = {}
    
    output_network_file.write("Node1\tNode2\tMzDiff\tCos_Score\tFileName\n");
    output_network_pairs_file.write("Node1\tNode2\tMzDiff\tCos_Score\tFileName\n");
    
    summary_line_count = 0
    
    for line in input_network_edges_file:
      splits = line.split()
      cluster_id_1 = int(splits[0])
      cluster_id_2 = int(splits[1])
      alignment_mz = float(splits[2]);
      alignment_cos = float(splits[4]);
      #output_network_file.write(line)
      output_network_file.write(str(cluster_id_1) + "\t" + str(cluster_id_2) + "\t" + str(alignment_mz) + "\t" + str(alignment_cos) + "\t" + path_to_specs_file + "\n");
      output_network_file.write(str(cluster_id_2) + "\t" + str(cluster_id_1) + "\t" + str(alignment_mz) + "\t" + str(alignment_cos) + "\t" + path_to_specs_file + "\n");
      
      output_network_pairs_file.write(str(cluster_id_1) + "\t" + str(cluster_id_2) + "\t" + str(alignment_mz) + "\t" + str(alignment_cos) + "\t" + path_to_specs_file + "\n");
      
      
    
    
if __name__ == "__main__":
    main()
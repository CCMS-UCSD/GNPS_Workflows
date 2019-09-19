#!/usr/bin/python


import sys
import getopt
import os



def usage():
    print "<input clustersummary> <input network edges> <output network egdes> <paramfiles>"
    
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
    
    input_summary_file = open(sys.argv[1], "r")
    input_network_edges_file = open(sys.argv[2], "r")
    output_network_file = open(sys.argv[3], "w")
    param_file = open(sys.argv[4], "r")
    params_map = parse_xml_file(param_file)
    min_cluster_size = int(params_map["CLUSTER_MIN_SIZE"])
    print "CLUSTER_MIN_SIZE " + str(min_cluster_size)
    #min_cluster_size = int(sys.argv[4])

    print "READING SUMMARY FILE"
    
    edges_already_in_network = {}
    
    summary_line_count = 0
    
    
    output_network_file.write("CLUSTERID1" + "\t" + "CLUSTERID2" + "\t" + "DeltaMZ" + "\t" + "MEH" +"\t" + "Cosine" + "\t" + "OtherScore" + "\t" + "ComponentIndex" + "\n");
    
    
    for line in input_network_edges_file:
      splits = line.split()
      cluster_id_1 = int(splits[0])
      cluster_id_2 = int(splits[1])
      edges_already_in_network[cluster_id_1] = 1
      edges_already_in_network[cluster_id_2] = 1
      output_network_file.write(line)
    
    for line in input_summary_file:
        summary_line_count += 1
        if summary_line_count == 1:
            continue
        
        splits = line.split()
        if int(splits[1]) >= min_cluster_size:
            cluster_id = splits[0]
            
            if int(cluster_id) in edges_already_in_network:
                #print "already in network"
                continue
            
            output_network_file.write(cluster_id + "\t" + cluster_id + "\t" + "0.0" + "\t" + "1.0" + "\t" + "1.0" + "\t" + "1.0" + "\t" + "-1" + "\n");
            #print line.rstrip()
        
        
        #return 0
            
            
    
    
    
if __name__ == "__main__":
    main()
#!/usr/bin/python


import sys
import getopt
import os
import math
from network_utils import MolecularNetwork, ClusterNode, NetworkPair
import networkx as nx


def parse_table_with_headers(filename):
    input_file = open(filename, "r")
    
    line_count = 0
    headers = []
    index_to_header_map = {}
    column_values = {}
    for line in input_file:
        line_count += 1
        if line_count == 1:
            headers = line.split("\t")
            header_idx = 0
            for header in headers:
                print header
                index_to_header_map[header_idx] = header
                header_idx += 1
                if len(header) > 1:
                    column_values[header] = []
            
            continue
        
        line_splits = line.split("\t")
        column_count = 0
        for line_split in line_splits:
            header_name = index_to_header_map[column_count]
            if len(header_name) < 1:
                continue
            column_values[header_name].append(line_split)
            column_count += 1
    
    return (line_count-1, column_values)



#Making sure directory exists, if not make it. 
def make_sure_path_exists(path):
    if not os.path.exists(directory):
        os.makedirs(directory)

def usage():
    print "<input pairs info> <clusterinfo file>"
    

def find_features_in_network(clusterinfo_filename, pairs_info_filename):
    #Creating molecular network
    molecular_network = MolecularNetwork("my network")
    molecular_network.load_clusterinfo_summary_file(clusterinfo_filename)
    molecular_network.load_pairs_file_noheaders(pairs_info_filename)
    
    get_mzdelta_topology_aware_clusters(molecular_network, [162], 1.0)
    
#Returns the the nodes which could exhibit topology indicative of structure features
def get_mzdelta_topology_aware_clusters(molecular_network, characteristic_mz_list, delta_tolerance):
    minimum_path_length = 3
    
    filtered_pairs = []
    
    for pair in molecular_network.all_pairs:
        pair_delta = math.fabs(float(pair.deltamz))
        #Checking if this guy is within tolerance
        acceptable_mz = False
        for characterisic_mz in characteristic_mz_list:
            if math.fabs(pair_delta - characterisic_mz) < delta_tolerance:
                acceptable_mz = True
                break
        
        if acceptable_mz == True:
            filtered_pairs.append(pair)
    
    print len(filtered_pairs)
    
    graph_nodes = {}
    directed_edges = []
    for pair in filtered_pairs:
        graph_nodes[pair.node1] = 1
        graph_nodes[pair.node2] = 1
        
        if molecular_network.cluster_to_nodedata[pair.node1].parentmass > molecular_network.cluster_to_nodedata[pair.node2].parentmass:
            directed_edges.append((pair.node1,pair.node2))
        else:
            directed_edges.append((pair.node2,pair.node1))
    
    
    G=nx.DiGraph()
    G.add_nodes_from(graph_nodes.keys())
    G.add_edges_from(directed_edges)
    
    candidate_nodes = []
    
    #Getting all pair shortest paths
    for source in graph_nodes.keys():
        for target in graph_nodes.keys():
            if source > target:
                #Upper Triangle
                try:
                    shortest_path = nx.shortest_path(G,source=source,target=target)
                    if len(shortest_path) >= minimum_path_length:
                        candidate_nodes.extend(shortest_path)
                        
                except nx.NetworkXNoPath:
                    continue
                
    #Removing list redundancy
    candidate_nodes = list(set(candidate_nodes))
    #print candidate_nodes
    
    #Grouping by component
    component_lists = {}
    for candidate_node in candidate_nodes:
        component_idx = molecular_network.cluster_to_nodedata[candidate_node].componentindex
        if component_idx != -1:
            if not (component_idx in component_lists):
                component_lists[component_idx] = []
            component_lists[component_idx].append(candidate_node)
          
    components_candidates = component_lists.keys()
    components_candidates.sort()
    print components_candidates
    print component_lists
    
    return None
    
def main():
    pairs_info_filename = sys.argv[1]
    clusterinfo_filename = sys.argv[2]
    
    find_features_in_network(clusterinfo_filename, pairs_info_filename)

    
if __name__ == "__main__":
    main()

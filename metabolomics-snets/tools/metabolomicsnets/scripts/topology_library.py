#!/usr/bin/python

import sys
import getopt
import os
import math
from molecular_network_library import MolecularNetwork, ClusterNode, NetworkPair
import networkx as nx
import ming_fileio_library
import json


def get_delta_path_key(delta_list):
    temp_list = []
    for delta in delta_list:
        temp_list.append(str(int(delta)))
    return "_".join(temp_list), "\t".join(temp_list)


def output_path_list(path_list_comprehensive, output_filename):
    output_header = "Delta1\tDelta2\tDelta3\tDeltaKey\tNodes"
    output_file = open(output_filename, "w")
    output_file.write(output_header)
    output_file.write("\n")
    #print output_header
    for path in path_list_comprehensive:
        delta_key, delta_tabbed = get_delta_path_key(path["delta_path"])
        output_line = delta_tabbed + "\t" + delta_key + "\t" + json.dumps(path["node_path"])
        #print output_line
        output_file.write(output_line)
        output_file.write("\n")

def output_path_list_histogram(path_list_comprehensive, output_filename):
    output_file = open(output_filename, "w")
    output_header = "delta_key\tcount\tDelta1\tDelta2\tDelta3"
    output_file.write(output_header)
    output_file.write("\n")
    #print output_header
    delta_counts = {}
    for path in path_list_comprehensive:
        delta_key, delta_tabbed = get_delta_path_key(path["delta_path"])
        if not delta_key in delta_counts:
            delta_counts[delta_key] = {"count" : 0, "delta_tabbed" : delta_tabbed}
        delta_counts[delta_key]["count"] += 1
    for key in delta_counts:
        output_line = key + "\t" + str(delta_counts[key]["count"]) + "\t" + str(delta_counts[key]["delta_tabbed"])
        output_file.write(output_line)
        output_file.write("\n")


def get_all_topology_paths(molecular_network, max_length):
    networkx_graph = create_networkx_graph(molecular_network.pairs, molecular_network.index_to_node_map)

    pairs_to_mz_delta_map = {}
    for pair in molecular_network.pairs:
        pair_key1 = str(pair.node1) + "_" + str(pair.node2)
        pair_key2 = str(pair.node2) + "_" + str(pair.node1)
        pairs_to_mz_delta_map[pair_key1] = pair.deltamz
        pairs_to_mz_delta_map[pair_key2] = pair.deltamz


    #Lets try doing a BFS
    # for node1 in molecular_network.nodes:
    #     if node1.component == -1:
    #         continue
    #     bfs list(nx.bfs_edges(networkx_graph, node1.index))

    all_paths_aggregate = []

    #Lets get all pairs of nodes in the same component
    node_count = 0
    for node1 in molecular_network.nodes:
        node_count += 1
        print "NODE INDEX: " + str(node1.index) + "\t" + str(node_count) + " out of " + str(len(molecular_network.nodes))
        for node2 in molecular_network.nodes:
            #print node1.component
            if node1.index == node2.index:
                continue
            if node1.component == -1 or node1.component == "-1":
                continue
            if node2.component == -1 or node2.component == "-1":
                continue
            if node1.component != node2.component:
                continue

            #Doing some shit
            all_paths = nx.all_simple_paths(networkx_graph, node1.index, node2.index, max_length)
            all_paths_list = list(all_paths)

            if len(all_paths_list) != 0:
                for path in all_paths_list:
                    if len(path) == max_length + 1:
                        all_paths_aggregate.append(path)


    #Lets make them unique and categorize the mass deltas
    unique_paths_map = {}
    for path in all_paths_aggregate:
        path_key = "_".join(path)
        unique_paths_map[path_key] = path

    #Now lets go ahead and categorize
    path_list_comprehensive = []
    path_delta_list = []
    for path_key in unique_paths_map:
        path_list = unique_paths_map[path_key]
        delta_list = []
        for i in range(len(path_list)-1):
            node1 = path_list[i]
            node2 = path_list[i+1]
            pair_key = str(node1) + "_" + str(node2)
            deltamz = pairs_to_mz_delta_map[pair_key]
            delta_list.append(abs(float(deltamz)))
        path_delta_list.append(delta_list)
        path_list_comprehensive.append({"node_path": path_list, "delta_path": delta_list})

    return path_list_comprehensive




def create_networkx_graph(pairs_list, index_to_nodes_map):
    filtered_pairs = pairs_list

    graph_nodes = {}
    directed_edges = []
    for pair in filtered_pairs:
        graph_nodes[pair.node1] = 1
        graph_nodes[pair.node2] = 1

        if index_to_nodes_map[pair.node1].mz > index_to_nodes_map[pair.node2].mz:
            directed_edges.append((pair.node1,pair.node2))
        else:
            directed_edges.append((pair.node2,pair.node1))

    G=nx.DiGraph()
    G.add_nodes_from(graph_nodes.keys())
    G.add_edges_from(directed_edges)

    return G

#Returns the the nodes which could exhibit topology indicative of structure features
def get_mzdelta_topology_aware_clusters(molecular_network, characteristic_mz_list, delta_tolerance):
    minimum_path_length = 3

    filtered_pairs = []

    for pair in molecular_network.pairs:
        pair_delta = math.fabs(float(pair.deltamz))
        #Checking if this guy is within tolerance
        acceptable_mz = False
        for characterisic_mz in characteristic_mz_list:
            if math.fabs(pair_delta - characterisic_mz) < delta_tolerance:
                acceptable_mz = True
                break

        if acceptable_mz == True:
            filtered_pairs.append(pair)

    graph_nodes = {}
    directed_edges = []
    for pair in filtered_pairs:
        graph_nodes[pair.node1] = 1
        graph_nodes[pair.node2] = 1

        if molecular_network.index_to_node_map[pair.node1].mz > molecular_network.index_to_node_map[pair.node2].mz:
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
        component_idx = molecular_network.index_to_node_map[candidate_node].component
        if component_idx != -1:
            if not (component_idx in component_lists):
                component_lists[component_idx] = []
            component_lists[component_idx].append(candidate_node)

    components_candidates = component_lists.keys()
    components_candidates.sort()
    print components_candidates
    print component_lists

    return None

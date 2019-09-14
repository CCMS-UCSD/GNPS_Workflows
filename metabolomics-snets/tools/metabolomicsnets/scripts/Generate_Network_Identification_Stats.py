#!/usr/bin/python


import sys
import getopt
import os

def usage():
    print "<input clusterinfosummary file> <input edges file> <outptu file> "
    
#Boiler Plate XML parsing
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
    reverse_mapping = {}
    for mapping in all_mappings:
        #print mapping
        splits = mapping.split("|")
        mangled_name = splits[0]
        original_name = splits[1]
        mangled_mapping[mangled_name] = original_name
        reverse_mapping[original_name] = mangled_name
    
    return mangled_mapping,reverse_mapping

#Stripping off prefix too
def filename_to_group_mapping(reverse_mapping):
    mapping = {}
    for filename in reverse_mapping:
        stripped_filname = os.path.basename(filename)
        mangled_name = reverse_mapping[filename]
        group_name = "G1"
        if mangled_name.find("spec-") != -1:
            group_name = "G1"
        if mangled_name.find("spectwo-") != -1:
            group_name = "G2"
        if mangled_name.find("specthree-") != -1:
            group_name = "G3"
        if mangled_name.find("specfour-") != -1:
            group_name = "G4"
        if mangled_name.find("specfive-") != -1:
            group_name = "G5"
        if mangled_name.find("specsix-") != -1:
            group_name = "G6"
            
        mapping[stripped_filname] = group_name
    return mapping

def load_clusterinfo_summary_file(filename):
    clusterinfo_file = open(filename, "r")
    
    count = 0
    cluster_to_is_map = {}
    cluster_to_nodedata_map = {}
    
    cluster_index_index = 0
    number_of_spectra_index = 1
    filename_string_index = 12
    identification_index = 19
    
    for line in clusterinfo_file:
        count += 1
        
        if count == 1:
            headers_list = line.split("\t")
            index_number = -1
            for header_item in headers_list:
                index_number += 1
                if header_item == "cluster index":
                    cluster_index_index = index_number
                    continue
                if header_item == "number of spectra":
                    number_of_spectra_index = index_number
                    continue
                if header_item == "AllFiles":
                    filename_string_index = index_number
                    continue
                if header_item == "LibraryID":
                    identification_index = index_number
                    continue
                
                
            continue
        
        splits = line.split("\t")
        cluster_index = splits[cluster_index_index]
        number_of_spectra = splits[number_of_spectra_index]
        filename_string = splits[filename_string_index]
        identification = splits[identification_index]
        cluster_to_is_map[cluster_index] = identification
        
        cluster_node = ClusterNode(identification, int(number_of_spectra), cluster_index, filename_string)
        cluster_to_nodedata_map[cluster_index] = cluster_node
        #if len(identification) > 3:
        #    print identification
        
    return cluster_to_nodedata_map
    
def get_number_of_nodes_identified(cluster_to_id_map):
    id_count = 0
    for key in cluster_to_id_map:
        if is_identified_identified(cluster_to_id_map[key].identification):
            id_count += 1
    return id_count
    
def get_list_of_nodes_identified(cluster_to_id_map):
    id_count = 0
    return_list = []
    for key in cluster_to_id_map:
        if is_identified_identified(cluster_to_id_map[key].identification):
            return_list.append(key)
    return return_list
    
def get_nodes_not_in_component(identified_nodes, node_component_map):
    nodes_not_in_components = []
    for id_node in identified_nodes:
        if not (id_node in node_component_map):
            nodes_not_in_components.append(id_node)
            
    return nodes_not_in_components
    
def get_identified_node_list(cluster_to_node_map):
    node_list = []
    for key in cluster_to_node_map:
        if is_identified_identified(cluster_to_node_map[key].identification):
            node_list.append(key)
    return node_list

def get_cluster_neighbor_map(network_pairs):
    cluster_neighbor_map = {}
    
    for pair in network_pairs:
        if not (pair.node1 in cluster_neighbor_map):
            cluster_neighbor_map[pair.node1] = []
        if not (pair.node2 in cluster_neighbor_map):
            cluster_neighbor_map[pair.node2] = []
        
        cluster_neighbor_map[pair.node1].append(pair.node2)
        cluster_neighbor_map[pair.node2].append(pair.node1)
        
    return cluster_neighbor_map


def get_component_to_node_map(network_pairs):
    component_node_map = {}
    node_component_map = {}
    
    for pair in network_pairs:
        if not (pair.component in component_node_map):
            component_node_map[pair.component] = []
        
        component_node_map[pair.component].append(pair.node2)
        component_node_map[pair.component].append(pair.node1)
        
        node_component_map[pair.node1] = pair.component
        node_component_map[pair.node2] = pair.component
        
    return component_node_map, node_component_map

def get_identified_components(node_component_map, identified_nodes):
    identified_components = []
    for id_node in identified_nodes:
        if id_node in node_component_map:
            identified_components.append(node_component_map[id_node])
            
    identified_components = list(set(identified_components))
    return identified_components

def get_unidentified_analog_list(identified_nodes, cluster_neighbor_map, cluster_to_id_map):
    possible_neighbor_of_id = []
    for id_node in identified_nodes:
        if id_node in cluster_neighbor_map:
            possible_neighbor_of_id = cluster_neighbor_map[id_node] + possible_neighbor_of_id
        
    unidentified_neighbors_of_id = []
    for possible_node in possible_neighbor_of_id:
        if not is_identified_identified(cluster_to_id_map[possible_node].identification):
            unidentified_neighbors_of_id.append(possible_node)
            
    #print possible_neighbor_of_id
    #print unidentified_neighbors_of_id
    #print list(set(unidentified_neighbors_of_id))
    return list(set(unidentified_neighbors_of_id))
    
def get_number_of_spectra_in_components_list(component_list, component_node_map):
    nodes_list = []
    
    for component_id in component_list:
        #print component_id
        #print component_node_map[component_id]
        #print len(component_node_map[component_id])
        nodes_list += component_node_map[component_id]

    return list(set(nodes_list))

class NetworkPair:
    def __init__(self, node1, node2, component):
        self.node1 = node1
        self.node2 = node2
        self.component = component

class ClusterNode:
    def __init__(self, identification, spectrum_count, clusterindex, filenames):
        self.clusterindex = clusterindex
        self.spectrum_count = spectrum_count
        self.identification = identification
        self.sourcefilestring = filenames

class InputFileSummary:
    def __init__(self, filename, list_of_cluster_indexes, group_string):
        self.filename = filename
        self.list_of_cluster_indexes = list_of_cluster_indexes
        self.group_string = group_string
        
    def __repr__(self):
        return self.filename + ":" + str(len(self.list_of_cluster_indexes))

#Returns a list of lists
def load_network_file(network_filename):
    network_file = open(network_filename, "r")
    
    network_pairs = []
    
    for line in network_file:
        splits = line.split("\t")
        node1 = splits[0]
        node2 = splits[1]
        component = splits[6].rstrip()
        cur_pair = NetworkPair(node1, node2, component)
        network_pairs.append(cur_pair)
        
    return network_pairs
    
def get_spectral_count_from_node_list(node_list, cluster_to_node_map):
    spectrum_counts = 0
    for node_idx in node_list:
        spectrum_counts += cluster_to_node_map[node_idx].spectrum_count
    
    return spectrum_counts
   
def int_is_bit_1_in_position(integer_value, bit_position):
    return (integer_value >> bit_position)&1
    
def is_identified_identified(input_name):
    if input_name ==  "N/A":
        return False
    if len(input_name) < 2:
        return False
    return True
        
    
    
    
def generate_rarefaction_curve(cluster_to_node_map, file_to_group_mapping, order_by_group):
    output_string = ""
    
    files_to_scans = {} 
    file_input_composition = {}
    for key in cluster_to_node_map:
        splits = cluster_to_node_map[key].sourcefilestring.split("###")
        all_files_for_node = []
        for spectrum_scan_string in splits:
            if len(spectrum_scan_string) < 2:
                continue
            right_colon_pos = spectrum_scan_string.rfind(":")
            spectrum_filename = spectrum_scan_string[:right_colon_pos]
            all_files_for_node.append(spectrum_filename)
            
            #Adding input file composition
            if not (spectrum_filename in file_input_composition):
                file_input_composition[spectrum_filename] = []
            file_input_composition[spectrum_filename].append(spectrum_scan_string.rstrip())
            
        all_files_for_node = list(set(all_files_for_node))
        
        #Iterate over all files per scan
        for filename_in_node in all_files_for_node:
            if not (filename_in_node in files_to_scans):
                files_to_scans[filename_in_node] = []
            files_to_scans[filename_in_node].append(cluster_to_node_map[key].clusterindex)
        
        
        #print cluster_to_node_map[key].sourcefilestring
        
    #Generating actual curve
    list_of_input_files = []
    for input_filenames in files_to_scans:
        list_of_input_files.append(InputFileSummary(input_filenames, files_to_scans[input_filenames], file_to_group_mapping[input_filenames]))
        
    if(order_by_group == False):
        list_of_input_files = sorted(list_of_input_files, key = lambda x:  len(x.list_of_cluster_indexes), reverse=True)
    else:
        #Order by group first and then order subgroup by number of cluster indices
        file_grouping = {}
        for file_info in list_of_input_files:
            if not (file_info.group_string in file_grouping):
                file_grouping[file_info.group_string] = []
            file_grouping[file_info.group_string].append(file_info)
        for group_string in file_grouping:
            file_grouping[group_string] = sorted(file_grouping[group_string], key = lambda x:  len(x.list_of_cluster_indexes), reverse=True)
        
        group_ordering = ["G1", "G2", "G3", "G4", "G5", "G6"]
        
        list_of_input_files = []
        for group_string in group_ordering:
            if group_string in file_grouping:
                list_of_input_files += file_grouping[group_string]
                
        #Generate Grouping Union of Scan Numbers
        spectra_per_group_mapping = {}
        for group_name in group_ordering:
            if not ( group_name in spectra_per_group_mapping ):
                spectra_per_group_mapping[group_name] = []
                
            if not group_name in file_grouping:
                continue
            
            for file_info in file_grouping[group_name]:
                spectra_per_group_mapping[group_name] += file_info.list_of_cluster_indexes
            #print group_name
            #spectra_per_group_mapping[group_name] = 
        
        output_string += "\n Venn Diagram\n"
        #Generate Venn Diagram
        for n in range(64):
            if n == 0:
                continue
            bit_position = 0
            #cumulative_list = []
            inclusion_lists = []
            difference_lists = []
            venn_output_string = ""
            for group_name in group_ordering:
                if int_is_bit_1_in_position(n, bit_position):
                    #union_list = list(set(union_list + spectra_per_group_mapping[group_name]))
                    inclusion_lists.append(spectra_per_group_mapping[group_name])
                    #cumulative_list = list(set(cumulative_list).intersection(spectra_per_group_mapping[group_name]))
                    #print "Include: " + group_name
                    venn_output_string += group_name + " AND " 
                else:
                    difference_lists.append(spectra_per_group_mapping[group_name])
                    #difference_list = list(set(difference_list + spectra_per_group_mapping[group_name]))
                    #cumulative_list = list(set(cumulative_list).difference(set(spectra_per_group_mapping[group_name])))
                bit_position += 1
            
            inclusion_intersection = set()
            if len(inclusion_lists) > 0:
                inclusion_intersection = set(inclusion_lists[0])
            for include_list in inclusion_lists:
                inclusion_intersection = inclusion_intersection.intersection(set(include_list))
            
            venn_output_string += "\t" + str(len(inclusion_intersection)) + "\n"
            output_string += venn_output_string
            print venn_output_string.rstrip()
            
                
    output_string +=  "\nRarefaction Curve" + "\n"
    output_string += "-----------------------------------------------------------" + "\n"
    output_string += "Filename\t#ClustersAffected\t#MarginalClusters\t#CumulativeClusters\tFileSpectra\tCumulativeFileSpectra\tGroup" + "\n"
    
    accumulated_cluster_indices = []
    cumulative_input_spectra_counts = 0
    for file_info in list_of_input_files:
        old_accumulated_size = len(accumulated_cluster_indices)
        cumulative_input_spectra_counts += len(file_input_composition[file_info.filename])
        accumulated_cluster_indices += file_info.list_of_cluster_indexes
        accumulated_cluster_indices = list(set(accumulated_cluster_indices))
        new_accumulated_size = len(accumulated_cluster_indices)
        output_string += file_info.filename + "\t" 
        output_string += str(len(file_info.list_of_cluster_indexes)) + "\t" 
        output_string += str(new_accumulated_size - old_accumulated_size) + "\t"
        output_string += str(new_accumulated_size) + "\t" 
        output_string += str(len(file_input_composition[file_info.filename])) + "\t"
        output_string += str(cumulative_input_spectra_counts) + "\t"
        output_string += file_info.group_string + "\n"
    
    #print output_string
    return output_string
    
    
def main():
    #usage()
    
    clusterinfo_filename = sys.argv[1]
    input_edges_filename = sys.argv[2]
    output_filename = sys.argv[3]
    param_xml_filename = sys.argv[4]
    
    #Reading param file
    param_mapping = parse_xml_file(open(param_xml_filename,"r"))
    mangled_mapping, reverse_mapping = get_mangled_file_mapping(param_mapping)
    file_to_group_mapping = filename_to_group_mapping(reverse_mapping)
    
    #Mapping Clusters to Nodes
    cluster_to_node_map = load_clusterinfo_summary_file(clusterinfo_filename)
    
    if len(cluster_to_node_map) == 0:
        output_file = open(output_filename, "w")
        output_file.write("No Clustering")
        return
    
    network_pairs = load_network_file(input_edges_filename)
    
    identified_nodes = get_identified_node_list(cluster_to_node_map)
    
    cluster_neighbor_map = get_cluster_neighbor_map(network_pairs)
    unidentified_neighbor_distance_1 = get_unidentified_analog_list(identified_nodes, cluster_neighbor_map, cluster_to_node_map)
    
    component_node_map, node_component_map = get_component_to_node_map(network_pairs)
    
    identified_components = get_identified_components(node_component_map, identified_nodes)
    #print identified_components
    
    all_nodes_in_network = get_number_of_spectra_in_components_list(component_node_map.keys(), component_node_map)
    all_nodes_in_identifed_components = get_number_of_spectra_in_components_list(identified_components, component_node_map)
    
    id_nodes_not_in_components = get_nodes_not_in_component(identified_nodes, node_component_map)

    #print len(total_nodes_in_network)
    #print component_node_map.keys()
    #print cluster_neighbor_map
    
    output_string = ""
    
    
    output_string +=  "Number of Nodes:\t" + str(len(cluster_to_node_map)) + "\n"
    output_string +=  "Number of pairs:\t" + str(len(network_pairs)) + "\n"
    output_string +=  "Number of ID'd clusternodes:\t" + str(len(get_list_of_nodes_identified(cluster_to_node_map))) + "\n"
    output_string +=  "Number of ID'd clusternodes not in components:\t" + str(len(id_nodes_not_in_components)) + "\n"
    output_string +=  "Number of unidentified neighbors:\t" + str(len(unidentified_neighbor_distance_1)) + "\n"
    output_string +=  "Number of connected components not single:\t" + str(len(component_node_map)) + "\n"
    output_string +=  "Number of clusternodes in network:\t" + str(len(all_nodes_in_network)) + "\n"
    output_string +=  "Number of connected components identified:\t" + str(len(identified_components)) + "\n"
    output_string +=  "Number of clusternodes in identified components:\t" + str(len(all_nodes_in_identifed_components)) + "\n"
    output_string +=  "-------------------------------------------------" + "\n"
    output_string +=  "Number of spectra in consideration:\t" + str(get_spectral_count_from_node_list(cluster_to_node_map.keys(), cluster_to_node_map)) + "\n"
    output_string +=  "Number of spectra in network:\t" + str(get_spectral_count_from_node_list(all_nodes_in_network, cluster_to_node_map)) + "\n"
    output_string +=  "Number of ID'd spectra:\t" + str(get_spectral_count_from_node_list(get_list_of_nodes_identified(cluster_to_node_map), cluster_to_node_map)) + "\n"
    output_string +=  "Number of ID'd spectra not in components:\t" + str(get_spectral_count_from_node_list(id_nodes_not_in_components, cluster_to_node_map)) + "\n"
    output_string +=  "Number of unidentified neighbor spectra:\t" + str(get_spectral_count_from_node_list(unidentified_neighbor_distance_1, cluster_to_node_map)) + "\n"
    output_string +=  "Number of spectra in identified components:\t" + str(get_spectral_count_from_node_list(all_nodes_in_identifed_components, cluster_to_node_map)) + "\n"
    
    print output_string
    output_file = open(output_filename, "w")
    output_file.write(output_string)
    
    output_string = generate_rarefaction_curve(cluster_to_node_map, file_to_group_mapping, False)
    output_file.write(output_string)
    
    
    output_string = generate_rarefaction_curve(cluster_to_node_map, file_to_group_mapping, True)
    output_file.write(output_string)
    
    
    
if __name__ == "__main__":
    main()

"""
Molecular Network Utilties For Use at GNPS

These classes provide utilies for loading and doing manipulation of the files
"""


class ClusterNode:
    def __init__(self, identification, spectrum_count, clusterindex, filenames, originalline, parentmass):
        self.clusterindex = clusterindex
        self.spectrum_count = spectrum_count
        self.identification = identification
        self.sourcefilestring = filenames
        self.originalstringline = originalline
        self.parentmass = parentmass
        self.componentindex = -1
        self.peptide = ""


class NetworkPair:
    def __init__(self, node1, node2, component, deltamz, cosine):
        self.node1 = node1
        self.node2 = node2
        self.deltamz = deltamz
        self.cosine = cosine
        self.component = component

class ConnectedComponent:
    def __init__(self):
        self.nodes = []
        self.componentindex = 0

    def get_number_of_nodes(self):
        return len(self.nodes)

    def get_number_of_spectra(self):
        total = 0
        for node in self.nodes:
            total += node.spectrum_count
        return total;

    def get_percent_nodes_id(self):
        total_id = 0
        for node in self.nodes:
            if len(node.identification) > 0 and node.identification != "N/A":
                total_id += 1

        #print str(total_id) + "\t" + str(self.get_number_of_nodes()) + "\t" + str(float(total_id)/float(self.get_number_of_nodes()))
        return float(total_id)/float(self.get_number_of_nodes())

    #returns a string of all the default groups
    def get_component_groups_default(self):
        groups = []
        for node in self.nodes:
            default_string = node.default_group
            default_groups = default_string.split(",")
            groups += default_groups
        groups = list(set(groups))
        filtered_groups = []
        for group in groups:
            if len(group) > 0:
                filtered_groups.append(group)
        return ",".join(filtered_groups)

    def get_component_groups_user(self):
        groups = []
        for node in self.nodes:
            group_string = node.user_group
            group_list = group_string.split(",")
            groups += group_list
        groups = list(set(groups))
        filtered_groups = []
        for group in groups:
            if len(group) > 0:
                filtered_groups.append(group)
        return ",".join(filtered_groups)


    def get_component_identifications(self):
        identifications = []
        for node in self.nodes:
            if node.identification == "N/A":
                continue

            if len(node.identification) > 0:
                identifications.append(node.identification)
        return_str = ("!".join(list(set(identifications))))
        if len(return_str) < 1:
            return_str = "N/A"
        return return_str

    def get_component_peptides(self):
        peptides = []
        for node in self.nodes:
            if node.peptide == "N/A":
                continue

            if len(node.peptide) > 0:
                peptides.append(node.peptide)
        return_str = ("!".join(list(set(peptides))))
        if len(return_str) < 1:
            return_str = "N/A"
        return return_str


class MolecularNetwork:
    def __init__(self, network_name):
        self.network_name = network_name
        self.all_pairs = []
        self.cluster_to_nodedata = []

    #Loading just the network nodes, pairs file directly out of pairsinfo, without headers, should be called after clusterinfo
    def load_pairs_file_noheaders(self, filename):
        all_pairs = []
        pairs_file = open(filename, "r")
        for line in pairs_file:
            splits = line.split("\t")
            node1 = splits[0]
            node2 = splits[1]
            deltamz = splits[2]
            cosine = splits[4]
            component_index = splits[6]
            pair_object = NetworkPair(node1, node2, component_index, deltamz, cosine)
            all_pairs.append(pair_object)
            if node1 in self.cluster_to_nodedata:
                self.cluster_to_nodedata[node1].componentindex = int(component_index)
                self.cluster_to_nodedata[node2].componentindex = int(component_index)

        self.all_pairs = all_pairs


    #Must be called after cluster info summary loading, if we want to populate the cluster_to_nodedata
    def load_identification_file(self, filename, populate_cluster_data):
        identification_file = open(filename, "r")

        scan_to_identification_map = {}
        count = 0

        cluster_index_index = 22
        identification_index = 0

        for line in identification_file:
            count += 1

            if count == 1:
                continue

            identification = line.split("\t")[identification_index]
            scan_number = line.split("\t")[cluster_index_index]
            scan_to_identification_map[scan_number] = identification

            if populate_cluster_data == True:
                self.cluster_to_nodedata[scan_number].identification = identification
        self.scan_to_identification = scan_to_identification_map

    #Returns the number of spectra in node list
    def get_number_of_spectra_in_nodes(self, node_list):
        total_count = 0
        for node in node_list:
            if node in self.cluster_to_nodedata:
                total_count += self.cluster_to_nodedata[node].spectrum_count
            else:
                total_count += 0
        return total_count

    #Returns the number of spectra in identifications
    def get_number_of_spectra_identified_in_nodes(self):
        node_list = self.scan_to_identification.keys()
        return self.get_number_of_spectra_in_nodes(node_list)


    #Loading the all peptide identification file from 2 pass workflow
    def load_peptide_identification_2pass(self, filename):
        number_results, identification_table = parse_table_with_headers(filename)
        scan_to_peptide_map = {}
        for i in range(number_results):
            cluster_index = identification_table["Cluster_index"][i]
            peptide = identification_table["Peptide"][i]
            #print cluster_index + "\t" + peptide
            self.cluster_to_nodedata[cluster_index].peptide = peptide



    #Loading clusterinfor summary file
    def load_clusterinfo_summary_file(self, filename):
        clusterinfo_file = open(filename, "r")

        count = 0
        cluster_to_nodedata_map = {}

        cluster_index_index = 0
        number_of_spectra_index = 1
        filename_string_index = 12
        identification_index = -1
        component_index = -1
        parentmass_index = -1
        default_group_index = -1
        user_group_index = -1

        for line in clusterinfo_file:
            count += 1

            if count == 1:
                headers_list = line.split("\t")
                self.clusterinfosummary_file_header = line.rstrip()
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
                    if header_item == "componentindex":
                        component_index = index_number
                        continue
                    if header_item == "parent mass":
                        parentmass_index = index_number
                        continue
                    if header_item == "AllGroups":
                        user_group_index = index_number
                        continue
                    if header_item == "DefaultGroups":
                        default_group_index = index_number
                        continue

                continue

            splits = line.split("\t")
            cluster_index = splits[cluster_index_index]
            number_of_spectra = splits[number_of_spectra_index]
            filename_string = splits[filename_string_index]
            parent_mass = float(splits[parentmass_index])

            default_group_string = splits[default_group_index]
            user_group_string = splits[user_group_index]

            if(identification_index != -1):
                identification = splits[identification_index]
                if len(identification) < 2:
                    identification = ""
            else:
                identification = ""

            cluster_node = ClusterNode(identification, int(number_of_spectra), cluster_index, filename_string, line.rstrip(), parent_mass)
            cluster_node.user_group = user_group_string
            cluster_node.default_group = default_group_string

            #Parsing component index
            if(component_index != -1):
                cluster_node.componentindex = int(splits[component_index])

            cluster_to_nodedata_map[cluster_index] = cluster_node


        self.cluster_to_nodedata = cluster_to_nodedata_map

    def get_number_of_spectra_per_node(self, node_index):
        if node_index in self.cluster_to_nodedata:
            return self.cluster_to_nodedata[node_index].spectrum_count
        return 0

    #Returns a list of all the connected components
    #Assumes that the component index has been populated either by loading the pairs file or that it already is in there because of the clusterinfosummary file
    def get_all_connected_components(self):
        component_map = {}
        for nodeindex in self.cluster_to_nodedata:
            component_index = self.cluster_to_nodedata[nodeindex].componentindex

            if(component_index == -1):
                continue

            if( not (component_index in component_map)):
                component_map[component_index] = ConnectedComponent()
                component_map[component_index].componentindex = component_index

            component_map[component_index].nodes.append(self.cluster_to_nodedata[nodeindex])

        return component_map.values()




#Parse a TSV File and then give an object back
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

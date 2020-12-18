#!/usr/bin/python


import sys
import getopt
import os
from operator import eq

import ming_fileio_library
import networkx as nx
import constants_network as CONST

def loading_network(filename, hasHeaders=False, edgetype="Cosine"):
    node1_list = []
    node2_list = []

    mass_difference = []
    property1 = []
    cosine_score = []
    explained_intensity = []
    edge_annotation = []

    if hasHeaders == True:
        row_count, table_data = ming_fileio_library.parse_table_with_headers(filename)

        if row_count == -1:
            return nx.MultiGraph()

        node1_list = table_data["CLUSTERID1"]
        node2_list = table_data["CLUSTERID2"]

        mass_difference = table_data["DeltaMZ"]
        property1 = table_data["MEH"]
        cosine_score = None
        if "Cosine" in table_data:
            cosine_score = table_data["Cosine"]
        if "COSINE" in table_data:
            cosine_score = table_data["COSINE"]
        
        if "OtherScore" in table_data:
            explained_intensity = table_data["OtherScore"]

        if len(property1)  != len(node1_list):
            property1 = node1_list
        if len(explained_intensity)  != len(node1_list):
            explained_intensity = node1_list
        if "EdgeAnnotation" in table_data:
            edge_annotation = table_data["EdgeAnnotation"]
        else:
            edge_annotation = [" "] * len(node1_list)

    else:
        row_count, table_data = ming_fileio_library.parse_table_without_headers(filename)

        if row_count == -1:
            return nx.MultiGraph()

        node1_list = table_data[0]
        node2_list = table_data[1]

        mass_difference = table_data[2]
        property1 = table_data[3]
        cosine_score = table_data[4]
        explained_intensity = table_data[5]
        edge_annotation = [" "] * len(node1_list)

    edge_property_map = {}
    edge_object_list = []
    intermediate_graph_nodes = set()
    intermediate_edges_to_add = []
    for i in range(row_count):
        edge_object = {}
        edge_object["node1"] = node1_list[i]
        edge_object["node2"] = node2_list[i]
        edge_object["mass_difference"] = mass_difference[i]
        edge_object["property1"] = property1[i]
        edge_object["cosine_score"] = float(cosine_score[i])
        edge_object["explained_intensity"] = float(explained_intensity[i])
        edge_object["component"] = -1
        edge_object["EdgeType"] = edgetype
        edge_object["EdgeAnnotation"] = edge_annotation[i].rstrip()
        edge_object["EdgeScore"] = float(cosine_score[i])

        edge_key = node1_list[i] + "-" + node2_list[i]

        edge_property_map[edge_key] = edge_object

        intermediate_graph_nodes.add(edge_object["node1"])
        intermediate_graph_nodes.add(edge_object["node2"])

        # set key to edgetype for options to remove edge later in case multiple edges are present
        edge_key_for_dict = CONST.EDGE.COSINE_TYPE
        intermediate_edges_to_add.append((edge_object["node1"], edge_object["node2"], edge_key_for_dict, edge_object))

    G=nx.MultiGraph()
    G.add_nodes_from(intermediate_graph_nodes)
    G.add_edges_from(intermediate_edges_to_add)

    return G

def add_additional_edges(G, path_to_supplemental_edges):
    edge_list = ming_fileio_library.parse_table_with_headers_object_list(path_to_supplemental_edges, delimiter=",")

    edges_to_add = []

    for additional_edge_row in edge_list:
        try:
            node1 = additional_edge_row["ID1"]
            node2 = additional_edge_row["ID2"]
            
            node1_mz = G.node[node1]["precursor mass"]
            node2_mz = G.node[node2]["precursor mass"]

            mass_difference = float(node1_mz) - float(node2_mz)

            edgetype = additional_edge_row["EdgeType"]
            score = additional_edge_row["Score"]
            annotation = additional_edge_row["Annotation"]

            edge_object = {}
            edge_object["node1"] = node1
            edge_object["node2"] = node2
            edge_object["EdgeType"] = edgetype
            edge_object["EdgeAnnotation"] = annotation.rstrip()
            edge_object["EdgeScore"] = float(score)
            edge_object["mass_difference"] = mass_difference

            #set key to edgetype for options to remove edge later
            edge_key = edgetype
            edges_to_add.append((node1, node2, edge_key, edge_object))
        except:
            print("Error Adding Edge")
            continue

    G.add_edges_from(edges_to_add)

    return G


def add_clusterinfo_summary_to_graph(G, cluster_info_summary_filename):
    row_count, table_data = ming_fileio_library.parse_table_with_headers(cluster_info_summary_filename)

    #Setting default metadata for nodes in network
    #for node in G.node:
    #    print(node)

    default_listed_columns = [("precursor mass", "float"), \
    ("charge", "int"), \
    ("parent mass", "float"), \
    ("number of spectra", "int"), \
    ("cluster index", "int"), \
    ("sum(precursor intensity)", "float"), \
    ("RTMean", "float"), \
    ("AllGroups", "string"), ("DefaultGroups", "string"), \
    ("RTConsensus", "float"), ("UniqueFileSources", "string")]

    optional_listed_columns = [("Correlated Features Group ID", "string"), \
    ("Annotated Adduct Features ID", "string"), \
    ("Best Ion", "string"), \
    ("neutral M mass", "float"), \
    ("MS2 Verification Comment", "string"), \
    ("ProteoSAFeClusterLink", "string"), \
    ("GNPSLinkout_Cluster", "string"), \
    ("GNPSLinkout_Network", "string"), ("componentindex", "string")]

    print("+++++++++++++++", nx.__version__)

    group_columns = ["G1", "G2", "G3", "G4", "G5", "G6"]

    for i in range(row_count):
        cluster_index = table_data["cluster index"][i]

        if cluster_index in G:
            for default_column in default_listed_columns:
                key_name = default_column[0]
                type_name = default_column[1]
                try:
                    if type_name == "float":
                        G.node[cluster_index][key_name] = float(table_data[key_name][i])
                    elif type_name == "int":
                        G.node[cluster_index][key_name] = int(table_data[key_name][i])
                    elif type_name == "string":
                        G.node[cluster_index][key_name] = str(table_data[key_name][i])
                except:
                    if type_name == "float":
                        G.node[cluster_index][key_name] = float("0.0")
                    elif type_name == "int":
                        G.node[cluster_index][key_name] = int("0")
                    elif type_name == "string":
                        G.node[cluster_index][key_name] = str("N/A")

            for group_name in group_columns:
                try:
                    G.node[cluster_index][group_name] = float(table_data[group_name][i])
                except:
                    G.node[cluster_index][group_name] = 0.0

            #Looking for all the groups
            for header in table_data:
                if header.find("GNPSGROUP") != -1:
                    try:
                        G.node[cluster_index][header] = float(table_data[header][i])
                    except:
                        try:
                            G.node[cluster_index][header] = int(table_data[header][i])
                        except:
                            G.node[cluster_index][header] = -1

            #Looking for all Attributes
            for header in table_data:
                if header.find("ATTRIBUTE_") != -1:
                    try:
                        G.node[cluster_index][header] = table_data[header][i]
                    except:
                        G.node[cluster_index][header] = ""

            #Looking for optional columns
            for optional_column in optional_listed_columns:
                key_name = optional_column[0]
                type_name = optional_column[1]

                if key_name in table_data:
                    try:
                        if type_name == "float":
                            G.node[cluster_index][key_name] = float(table_data[key_name][i])
                        elif type_name == "int":
                            G.node[cluster_index][key_name] = int(table_data[key_name][i])
                        elif type_name == "string":
                            G.node[cluster_index][key_name] = str(table_data[key_name][i])
                    except:
                        if type_name == "float":
                            G.node[cluster_index][key_name] = float("0.0")
                        elif type_name == "int":
                            G.node[cluster_index][key_name] = int("0")
                        elif type_name == "string":
                            G.node[cluster_index][key_name] = str("N/A")



def add_library_search_results_to_graph(G, library_search_filename, annotation_prefix=""):
    row_count, table_data = ming_fileio_library.parse_table_with_headers(library_search_filename)

    for i in range(row_count):
        cluster_index = table_data["#Scan#"][i]

        if cluster_index in G.node:
            G.node[cluster_index][annotation_prefix + "Adduct"] = str(table_data["Adduct"][i].encode('ascii', 'ignore'))
            G.node[cluster_index][annotation_prefix + "Compound_Name"] = str(''.join([j if ord(j) < 128 else ' ' for j in table_data["Compound_Name"][i]]).replace("\\", "\\\\"))
            G.node[cluster_index][annotation_prefix + "Adduct"] = str(table_data["Adduct"][i])
            G.node[cluster_index][annotation_prefix + "INCHI"] = str(''.join([j if ord(j) < 128 else ' ' for j in table_data["INCHI"][i]]).replace("\\", "\\\\"))
            G.node[cluster_index][annotation_prefix + "Smiles"] = str(''.join([j if ord(j) < 128 else ' ' for j in table_data["Smiles"][i]]).replace("\\", "\\\\"))
            G.node[cluster_index][annotation_prefix + "MQScore"] = str(table_data["MQScore"][i])
            G.node[cluster_index][annotation_prefix + "MassDiff"] = str(table_data["MassDiff"][i])
            G.node[cluster_index][annotation_prefix + "MZErrorPPM"] = str(table_data["MZErrorPPM"][i])
            G.node[cluster_index][annotation_prefix + "SharedPeaks"] = str(table_data["SharedPeaks"][i])
            G.node[cluster_index][annotation_prefix + "tags"] = str(''.join([j if ord(j) < 128 else ' ' for j in table_data["tags"][i]]).replace("\\", "\\\\"))
            G.node[cluster_index][annotation_prefix + "Library_Class"] = str(table_data["Library_Class"][i])
            G.node[cluster_index][annotation_prefix + "Instrument"] = str(table_data["Instrument"][i])
            G.node[cluster_index][annotation_prefix + "IonMode"] = str(table_data["IonMode"][i])
            G.node[cluster_index][annotation_prefix + "Ion_Source"] = str(table_data["Ion_Source"][i])
            G.node[cluster_index][annotation_prefix + "PI"] = str(table_data["PI"][i])
            G.node[cluster_index][annotation_prefix + "Data_Collector"] = str(table_data["Data_Collector"][i])
            G.node[cluster_index][annotation_prefix + "Compound_Source"] = str(table_data["Compound_Source"][i])
            G.node[cluster_index][annotation_prefix + "SpectrumID"] = str(table_data["SpectrumID"][i])
            G.node[cluster_index][annotation_prefix + "GNPSLibraryURL"] = "http://gnps.ucsd.edu/ProteoSAFe/gnpslibraryspectrum.jsp?SpectrumID=" + table_data["SpectrumID"][i]

            try:
                # ion identity networking specific:
                # check best ion (ion identity) and adduct for similarity
                adduct = G.node[cluster_index][annotation_prefix + CONST.NODE.ADDUCT_LIB_ATTRIBUTE]
                ion_identity = G.node[cluster_index][CONST.NODE.IIN_ADDUCT_ATTRIBUTE]
                if ion_identity is not None and len(ion_identity)>0 and adduct is not None and len(adduct) > 0:
                    G.node[cluster_index][annotation_prefix + CONST.NODE.IIN_ADDUCT_EQUALS_LIB_ATTRIBUTE] = equal_adducts(adduct, ion_identity)
            except:
                pass


def equal_adducts(a, b):
    """
    Checks if two adducts are equal. Uses clean_adduct to harmonize notation
    :param a:
    :param b:
    :return: True or False
    """
    if a is None or b is None or len(a)<=0 or len(b)<=0:
        return False

    ca = clean_adduct(a)
    cb = clean_adduct(b)

    if ca is None or cb is None or len(ca)<=0 or len(cb)<=0:
        return False

    if ca == cb:
        return True

    if ca[-1] == '-' and cb[-1] != '+':
        ca = ca[:-1]
        return ca == cb
    if ca[-1] == '+' and cb[-1] != '-':
        ca = ca[:-1]
        return ca == cb
    if cb[-1] == '-' and ca[-1] != '+':
        cb = cb[:-1]
        return ca == cb
    if cb[-1] == '+' and ca[-1] != '-':
        cb = cb[:-1]
        return ca == cb
    return False


def clean_adduct(adduct, add_brackets=False):
    """
    Harmonizes adducts.
    :param adduct:
    :param add_brackets: add [M+H]+ brackets that are removed during clean up (True or False)
    :return: M-all losses+all additions CHARGE
    """
    new_adduct = adduct
    new_adduct = new_adduct.replace("[", "")
    new_adduct = new_adduct.replace("]", "")
    new_adduct = new_adduct.replace(" ", "")

    charge = ""
    charge_sign = ""
    for i in reversed(range(len(new_adduct))):
        if new_adduct[i] == "+" or new_adduct[i] == "-":
            charge_sign = new_adduct[i]
        elif new_adduct[i].isdigit():
            charge = new_adduct[i] + charge
        else:
            new_adduct = new_adduct[0:i + 1]
            break

    parts = new_adduct.split("+")
    positive_parts = []
    negative_parts = []
    for p in parts:
        sp = p.split("-")
        positive_parts.append(sp[0])
        for n in sp[1:]:
            negative_parts.append(n)
    # sort
    m_part = positive_parts[0]
    positive_parts = positive_parts[1:]
    positive_parts.sort()
    negative_parts.sort()
    new_adduct = m_part
    if len(negative_parts) > 0:
        new_adduct += "-" + "-".join(negative_parts)
    if len(positive_parts) > 0:
        new_adduct += "+" + "+".join(positive_parts)
    if add_brackets:
        new_adduct = "[" + new_adduct + "]"
    new_adduct += charge + charge_sign
    return new_adduct


def filter_top_k(G, top_k):
    print("Filter Top_K", top_k)
    #Keeping only the top K scoring edges per node
    print("Starting Numer of Edges", len(G.edges()))

    node_cutoff_score = {}
    for node in G.nodes():
        node_edges = G.edges((node), data=True)
        node_edges = sorted(node_edges, key=lambda edge: edge[2]["cosine_score"], reverse=True)

        edges_to_delete = node_edges[top_k:]
        edges_to_keep = node_edges[:top_k]

        if len(edges_to_keep) == 0:
            continue

        node_cutoff_score[node] = edges_to_keep[-1][2]["cosine_score"]

        #print("DELETE", edges_to_delete)


        #for edge_to_remove in edges_to_delete:
        #    G.remove_edge(edge_to_remove[0], edge_to_remove[1])


    #print("After Top K", len(G.edges()))
    #Doing this for each pair, makes sure they are in each other's top K
    edge_to_remove = []
    for edge in G.edges(data=True):
        cosine_score = edge[2]["cosine_score"]
        threshold1 = node_cutoff_score[edge[0]]
        threshold2 = node_cutoff_score[edge[1]]

        if cosine_score < threshold1 or cosine_score < threshold2:
            edge_to_remove.append(edge)

    for edge in edge_to_remove:
        G.remove_edge(edge[0], edge[1])

    print("After Top K Mutual", len(G.edges()))

def filter_component(G, max_component_size):
    if max_component_size == 0:
        return

    big_components_present = True

    while big_components_present == True:
        big_components_present = False
        components = nx.connected_components(G)
        for component in components:
            if len(component) > max_component_size:
                prune_component(G, component)
                big_components_present = True
        print("After Round of Component Pruning", len(G.edges()))

# This enables filtering of network components 
# but instead of breaking apart big components, 
# it adds edges only if it doesnt make too large components
def filter_component_additive(G, max_component_size):
    if max_component_size == 0:
        return

    all_edges = list(G.edges(data=True))
    G.remove_edges_from(list(G.edges))

    all_edges = sorted(all_edges, key=lambda x: x[2]["EdgeScore"], reverse=True)

    for edge in all_edges:
        G.add_edges_from([edge])
        largest_cc = max(nx.connected_components(G), key=len)

        if len(largest_cc) > max_component_size:
            G.remove_edge(edge[0], edge[1])
    
    

def get_edges_of_component(G, component):
    component_edges = {}
    for node in component:
        node_edges = G.edges((node), data=True)
        for edge in node_edges:
            if edge[0] < edge[1]:
                key = edge[0] + "-" + edge[1]
            else:
                key = edge[1] + "-" + edge[0]
            component_edges[key] = edge

    component_edges = component_edges.values()
    return component_edges

def prune_component(G, component, cosine_delta=0.02):
    component_edges = get_edges_of_component(G, component)

    min_score = 1000
    for edge in component_edges:
        min_score = min(min_score, edge[2]["cosine_score"])

    cosine_threshold = cosine_delta + min_score
    for edge in component_edges:
        if edge[2]["cosine_score"] < cosine_threshold:
            #print(edge)
            G.remove_edge(edge[0], edge[1])


def output_graph_with_headers(G, filename):
    output_list = []

    #Outputting the graph
    component_index = 0
    for component in nx.connected_components(G):
        component_index += 1
        for edge in get_edges_of_component(G, component):
            output_dict = {}

            if int(edge[0]) < int(edge[1]):
                output_dict["CLUSTERID1"] = edge[0]
                output_dict["CLUSTERID2"] = edge[1]
            else:
                output_dict["CLUSTERID1"] = edge[1]
                output_dict["CLUSTERID2"] = edge[0]

            output_dict["DeltaMZ"] = edge[2]["mass_difference"]
            output_dict["Cosine"] = edge[2]["cosine_score"]
            output_dict["ComponentIndex"] = component_index

            output_list.append(output_dict)

    ming_fileio_library.write_list_dict_table_data(output_list, filename)


def output_graph(G, filename):
    output_file = open(filename, "w")
    #Outputting the graph
    component_index = 0
    for component in nx.connected_components(G):
        component_index += 1
        for edge in get_edges_of_component(G, component):
            output_list = []
            if int(edge[0]) < int(edge[1]):
                output_list.append(edge[0])
                output_list.append(edge[1])
            else:
                output_list.append(edge[1])
                output_list.append(edge[0])
            output_list.append(edge[2]["mass_difference"])
            output_list.append(edge[2]["property1"])
            output_list.append(str(edge[2]["cosine_score"]))
            output_list.append(str(edge[2]["explained_intensity"]))
            output_list.append(str(component_index))
            output_file.write("\t".join(output_list) + "\n")

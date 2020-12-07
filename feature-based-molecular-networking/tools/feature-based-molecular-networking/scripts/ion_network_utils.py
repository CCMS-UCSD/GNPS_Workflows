#!/usr/bin/python
from networkx import nx
import logging_utils
import constants_network as CONST
import operator

logger = logging_utils.get_logger(__name__)

class TOOL:
    MZMINE = 1
    MSDIAL = 2
    XCMS_CAMERA = 3




def collapse_ion_networks(G, best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE,
                          edge_comparator=operator.ge):
    """
    Collapse all ion identity networks. Does nothing if no ion identity networks are available.
    Does not change G, returns a copy.
    :param G: networkx graph (MultiGraph)
    :param best_edge_att: attribute to find best edge for edge merging
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    :return: A copy of G with collapsed ion identity networks
    """
    H = G.copy()

    # todo calculate ion network ID for MS-DIAL and XCMS edges
    tool = check_iin_tool(H)
    if tool == TOOL.MSDIAL:
        calc_ion_net_id(G, CONST.EDGE.ION_MS_DIAL_TYPE)
    elif tool == TOOL.XCMS_CAMERA:
        calc_ion_net_id(G, CONST.EDGE.ION_TYPE)

    # remove all ion edges - they are not needed for collapsing
    remove_all_ion_edges(H)

    # collapse all nodes with the same ion network ID into the node with the highest abundance
    collapse_based_on_node_attribute(H, CONST.NODE.ION_NETWORK_ID_ATTRIBUTE, CONST.NODE.ABUNDANCE_ATTRIBUTE,
                                     best_edge_att, edge_comparator)

    # return copy of network G
    return H


def calc_ion_net_id(G, edge_type):
    current_id = 0
    for node, ndata in G.nodes(data=True):
        ion_net_id = get_ion_net_id(G, node, ndata)
        if ion_net_id is None:
            filtered_neighbors = G.neighbors(node)
            for n2 in filtered_neighbors:
                edges = G.get_edge_data(node, n2)
                for key, edata in edges.items():
                    if edata.get(CONST.EDGE.TYPE_ATTRIBUTE) == edge_type:
                        set_ion_net_id(G, edge_type, [node], node, current_id)
                        current_id += 1
                        break

def set_ion_net_id(G, edge_type, ion_net, current_node, id):
    # set ion net id
    G.nodes[current_node][CONST.NODE.ION_NETWORK_ID_ATTRIBUTE] = id
    filtered_neighbors = G.neighbors(current_node)
    for n2 in filtered_neighbors:
        if n2 not in ion_net:
            edges = G.get_edge_data(current_node, n2)
            for key, edata in edges.items():
                if edata.get(CONST.EDGE.TYPE_ATTRIBUTE) == edge_type:
                    ion_net.append(n2)
                    set_ion_net_id(G, edge_type, ion_net, n2, id)
                    break



def check_iin_tool(G):
    has_ion_net_id = False
    for node, ndata in G.nodes(data=True):
        ion_net_id = get_ion_net_id(G, node, ndata)
        if ion_net_id is not None:
            has_ion_net_id = True

        filtered_neighbors = G.neighbors(node)
        for n2 in filtered_neighbors:
            edges = G.get_edge_data(node, n2)
            for key, edata in edges.items():
                edge_type = edata.get(CONST.EDGE.TYPE_ATTRIBUTE)
                # edge and node has attribute
                if has_ion_net_id and edge_type == CONST.EDGE.ION_TYPE:
                    return TOOL.MZMINE
                # only edge has type
                elif edge_type == CONST.EDGE.ION_TYPE:
                    return TOOL.XCMS_CAMERA
                elif edge_type == CONST.EDGE.ION_MS_DIAL_TYPE:
                    return TOOL.MSDIAL
    return None




def collapse_based_on_node_attribute(H, merge_att, best_node_att, best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE,
                                     edge_comparator=operator.ge):
    """
    Collapse all nodes with the same merge_att=value.
    :param H: networkx graph (MultiGraph)
    :param merge_att: attribute to group nodes and merge them into a single node (all nodes with the same value)
    :param best_node_att: attribute to rank the nodes and merge all into the one with the highest value for this
    :param best_edge_att: attribute to find best edge (for edge merging - standard=constants.EDGE.SCORE)
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    """
    # store all nodes of ion identity networks as: ion_network_id -> list of nodes
    sub_networks_dict = {}
    for node, attributes in H.nodes(data=True):
        # has ion identity network ID? Add to list of nodes to reconstruct IIN
        if merge_att in attributes:
            sub_network_id = attributes[merge_att]
            if sub_network_id is not None and len(str(sub_network_id).strip()) > 0:
                nodes = []
                if sub_network_id in sub_networks_dict:
                    nodes = sub_networks_dict[sub_network_id]
                    nodes.append(node)
                else:
                    nodes = [node]
                sub_networks_dict[sub_network_id] = nodes

    # only >1 elements
    sorted_sub_networks = [net for net in sub_networks_dict.values() if len(net) > 1]
    # sort by number of nodes in ion identity network
    sorted_sub_networks = sorted(sorted_sub_networks, key=lambda net: len(net), reverse=True)
    logger.info("Number of sub networks for attribute (%s): %s", merge_att, len(sorted_sub_networks))

    # merge all into the node with the highest abundance
    reduced_nodes_count = 0
    for network in sorted_sub_networks:
        if len(network) > 1:  # only collapse networks with >1 nodes
            reduced_nodes_count += len(network)
            sorted_nodes = sorted(network, key=lambda ion_node: H.nodes[ion_node][best_node_att],
                                  reverse=True)
            merge_nodes(H, sorted_nodes, CONST.NODE.COLLAPSED_TYPE, True, best_edge_att, edge_comparator)
    logger.info("Collapsed %s nodes into %s remaining nodes", reduced_nodes_count, len(sorted_sub_networks))


def merge_nodes(G, nodes, new_node_type=CONST.NODE.COLLAPSED_TYPE, add_ion_intensity_attributes=True,
                best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE, edge_comparator=operator.ge):
    """
    Merges all nodes into the first element of nodes, redirects the edges to this node and removes the other nodes
    from the graph.
    Only a few attributes are transferred.
    :param G: networkx graph (MultiGraph)
    :param nodes: sorted list of nodes to be merged (first remains - all other nodes are merged into the first node)
    :param new_node_type: defines the node type of the collapsed main node (CONST.NODE.TYPE_ATTRIBUTE)
    :param add_ion_intensity_attributes: True or False; Adds intensity column (attribute) for each ion in this group
    :param best_edge_att: attribute to find best edge (for edge merging - standard=constants.EDGE.SCORE)
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    of merged nodes.
    """
    main_node = nodes[0]
    G.nodes[main_node][CONST.NODE.TYPE_ATTRIBUTE] = new_node_type
    G.nodes[main_node][CONST.NODE.COLLAPSED_NODES_ATTRIBUTE] = len(nodes)
    # combine node attributed
    # intensity for each ion adduct
    sum_intensity = 0.0
    for node in nodes:
        if CONST.NODE.ABUNDANCE_ATTRIBUTE in G.nodes[node]:
            intensity = G.nodes[node][CONST.NODE.ABUNDANCE_ATTRIBUTE]
            sum_intensity += intensity
            # add columns for each
            if add_ion_intensity_attributes and CONST.NODE.ADDUCT_ATTRIBUTE in G.nodes[node]:
                ion = G.nodes[node][CONST.NODE.ADDUCT_ATTRIBUTE]
                G.nodes[main_node][ion + CONST.NODE.SPECIFIC_ION_ABUNDANCE_ATTRIBUTE] = intensity
        # TODO handle more attributes: How to add multiple library matches to this one node? Keep match with highest
        #  score?

    # add sum of ion intensities
    G.nodes[main_node][CONST.NODE.SUM_ION_INTENSITY_ATTRIBUTE] = sum_intensity

    # redirect all edges to the first node and remove nodes
    redirect_edges_and_delete_nodes(G, nodes[1:], main_node, best_edge_att, edge_comparator)


def redirect_edges_and_delete_nodes(G, nodes, target_node, best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE, edge_comparator=operator.ge):
    """
    Redirect all edges to target_node and delete the list of nodes

    :param G: networkx graph (MultiGraph)
    :param nodes: list of nodes to be merged into target_node. Edges are redirect and nodes are deleted
    :param target_node: all edges are redirected to this node
    :param best_edge_att: attribute to find best edge
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    """
    for n1 in nodes:
        filtered_neighbors = [n for n in G.neighbors(n1) if n is not target_node]
        for n2 in filtered_neighbors:
            edges_to_add = []
            edges_to_remove = []

            edges = G.get_edge_data(n1, n2)
            target_edges = G.get_edge_data(target_node, n2)
            for key, data in edges.items():
                # target already contains edge with this type
                if target_edges is not None and key in target_edges:
                    if not (best_edge_att in data and best_edge_att in target_edges[key]):
                        logger.warn("Edges of key=%s do not contain attribute to score and merge edges: %s", key, best_edge_att)
                    elif edge_comparator(data[best_edge_att], target_edges[key][best_edge_att]):
                        # exchange edge
                        edges_to_add.append((target_node, n2, key, data))
                        edges_to_remove.append((n1, n2, key))
                        edges_to_remove.append((target_node, n2, key))
                        #logger.debug("Exchange edge with key "+str(key))
                else:
                    # add as new edge
                    edges_to_add.append((target_node, n2, key, data))
                    edges_to_remove.append((n1, n2, key))
                    #logger.debug("Adding edge with key "+str(key))
            # remove and add edges
            G.remove_edges_from(edges_to_remove)
            G.add_edges_from(edges_to_add)

    for n in nodes:  # remove the merged nodes
        if n is not target_node:
            G.remove_node(n)

def remove_all_ion_edges(G):
    """
    Removes all ion edges from ion identity networking (used prior to network collapsing)
    :param G: networkx graph (MultiGraph)
    """
    remove_all_edges_of_type(G, CONST.EDGE.ION_TYPE)
    remove_all_edges_of_type(G, CONST.EDGE.ION_MS_DIAL_TYPE)

def remove_all_edges_of_type(G, edge_type):
    """
    Removes all edges from a specific edge type (CONST.EDGE.TYPE_ATTRIBUTE)
    :param G: networkx graph (MultiGraph)
    :param edge_type: Remove all edges of this type
    """
    remove_all_edges(G, CONST.EDGE.TYPE_ATTRIBUTE, edge_type, equals_ignore_case)

def remove_all_edges(G, attribute, target_value, compare_function=lambda a,b: equals_ignore_case(a,b)):
    """
    Remove all edges based on the value of edge[attribute] and a compare_function(target,value). Standard function
    uses equals_ignore_case
    :param G: networkx graph (MultiGraph)
    :param attribute:
    :param target_value:
    :param compare_function: Standard function(target,value) compares lower case strings and removes all edges with
    edge[
    attribute] == value
    """
    logger.debug("Removing edges based on attribute[%s] and value=%s", attribute,target_value)
    edges_to_remove = []
    for n1, n2, key, data in G.edges(keys=True, data=True):
        # remove all edges with EDGE_TYPE_ATTRIBUTE = ION_EDGE_TYPE
        if attribute in data and compare_function(target_value, data[attribute]):
            edges_to_remove.append((n1, n2, key))
    G.remove_edges_from(edges_to_remove)
    logger.info("Removed %s edges for attribute[%s]", len(edges_to_remove), attribute)


def get_ion_net_id(G, node):
    """
    The ion network id or None if not present
    :param G: networkx graph
    :param node: node id
    :return:
    """
    try:
        return get_ion_net_id(G, node, G.nodes[node])
    except:
        return None

def get_ion_net_id(G, node, data):
    """
    The ion network id or None if not present
    :param G: networkx graph
    :param node: node id
    :param data: node data dict
    :return:
    """
    id = data.get(CONST.NODE.ION_NETWORK_ID_ATTRIBUTE)
    if id is not None and len(str(id))<=0:
        return None
    else:
        return id


def mark_all_node_types(G):
    """
    Marks all nodes as feature nodes or ion identity nodes (constants.NODE.TYPE_ATTRIBUTE)
    :param G: networkx graph (MultiGraph)
    """
    for node, data in G.nodes(data=True):
        # only set type if not already set
        if CONST.NODE.TYPE_ATTRIBUTE not in data:
            # ion identity node or feature node?
            ion_net_id = get_ion_net_id(G, node)
            if ion_net_id is not None:
                G.nodes[node][CONST.NODE.TYPE_ATTRIBUTE] = CONST.NODE.ION_TYPE
            else:
                G.nodes[node][CONST.NODE.TYPE_ATTRIBUTE] = CONST.NODE.FEATURE_TYPE

def equals_ignore_case(a, b):
    return str(a).lower().strip() == str(b).lower().strip()
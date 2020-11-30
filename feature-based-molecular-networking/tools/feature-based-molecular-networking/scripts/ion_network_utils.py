#!/usr/bin/python
from networkx import nx
import logging_utils
import constants as CONST
import operator

logger = logging_utils.get_logger(__name__)


def collapse_ion_networks(G, is_remove_duplicate_edges=True, best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE,
                          edge_comparator=operator.ge):
    """
    Collapse all ion identity networks. Does nothing if no ion identity networks are available.
    Does not change G, returns a copy.
    :param G: networkx graph (MultiGraph)
    :param is_remove_duplicate_edges: After collapsing sub networks - remove duplicate edges with the same edge_type -
    keep edges based on best_edge_att and the comparator function
    :param best_edge_att: attribute to find best edge
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    :return: A copy of G with collapsed ion identity networks
    """
    H = G.copy()

    # remove all ion edges - they are not needed for collapsing
    remove_all_ion_edges(H)

    # collapse all nodes with the same ion network ID into the node with the highest abundance
    collapse_based_on_node_attribute(H, CONST.NODE.ION_NETWORK_ID_ATTRIBUTE, CONST.NODE.ABUNDANCE_ATTRIBUTE,
                                     is_remove_duplicate_edges, best_edge_att, edge_comparator)

    # return copy of network G
    return H


def collapse_based_on_node_attribute(H, merge_att, best_node_att, is_remove_duplicate_edges=True,
                                     best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE, edge_comparator=operator.ge):
    """
    Collapse all nodes with the same merge_att=value.
    :param H: networkx graph (MultiGraph)
    :param merge_att: attribute to group nodes and merge them into a single node (all nodes with the same value)
    :param best_node_att: attribute to rank the nodes and merge all into the one with the highest value for this
    :param is_remove_duplicate_edges: After collapsing sub networks - remove duplicate edges with the same edge_type -
    keep edges based on best_edge_att and the comparator function
    :param best_edge_att: attribute to find best edge
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
            merge_nodes(H, sorted_nodes, CONST.NODE.COLLAPSED_TYPE, True)
    logger.info("Collapsed %s nodes into %s remaining nodes", reduced_nodes_count, len(sorted_sub_networks))

    # remove duplicate edges. Standard based on EDGE_SCORE - keep edge with max score
    if is_remove_duplicate_edges:
        remove_duplicate_edges(H, best_edge_att, edge_comparator)


def merge_nodes(G, nodes, new_node_type=CONST.NODE.COLLAPSED_TYPE, add_ion_intensity_attributes=True):
    """
    Merges all nodes into the first element of nodes, redirects the edges to this node and removes the other nodes
    from the graph.
    Only a few attributes are transferred.
    :param G: networkx graph (MultiGraph)
    :param nodes: sorted list of nodes to be merged (first remains - all other nodes are merged into the first node)
    :param new_node_type: defines the node type of the collapsed main node (CONST.NODE.TYPE_ATTRIBUTE)
    :param add_ion_intensity_attributes: True or False; Adds intensity column (attribute) for each ion in this group
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
    redirect_edges_and_delete_nodes(G, nodes[1:], main_node)


def redirect_edges_and_delete_nodes(G, nodes, target_node):
    """
    Redirect all edges to target_node and delete the list of nodes

    :param G: networkx graph (MultiGraph)
    :param nodes: list of nodes to be merged into target_node. Edges are redirect and nodes are deleted
    :param target_node: all edges are redirected to this node
    """
    edges_to_add = []
    for n1, n2, key, data in G.edges(keys=True, data=True):
        # no need to reconnect edges from n to target_node
        if n1 is not target_node and n2 is not target_node:
            # For all edges related to one of the nodes to merge,
            # make an edge going to or coming from the new node
            try:
                if n1 in nodes:
                    edges_to_add.append((target_node, n2, key, data))

                elif n2 in nodes:
                    edges_to_add.append((n1, target_node, key, data))
            except:
                logger.error("Error Adding Edge")
                continue
    # reconnect edges
    G.add_edges_from(edges_to_add)

    for n in nodes:  # remove the merged nodes
        if n is not target_node:
            G.remove_node(n)


def remove_duplicate_edges(G, best_edge_att=CONST.EDGE.SCORE_ATTRIBUTE, edge_comparator=operator.ge):
    """
    Remove duplicate edges between nodes after merging (edges of the same type)
    Keeps the highest score.
    :param G:
    :param best_edge_att: attribute to find best edge
    :param edge_comparator: function(a,b) specifies how to compare values - standard is operator.ge (a>=b)
    """
    #edges_to_remove = []
    #for n1 in G.nodes(data=True):
    #   for n2 in nx.neighbors(G, n1):
    #     for n1, n2, key, data in G.edges(keys=True, data=True):
    # remove all edges with EDGE_TYPE_ATTRIBUTE = ION_EDGE_TYPE
    #   if EDGE_TYPE_ATTRIBUTE in data and str(data[EDGE_TYPE_ATTRIBUTE]).lower().strip() == ION_EDGE_TYPE:
    #       edges_to_remove.append((n1, n2, key))
    #G.remove_edges_from(edges_to_remove)


def remove_all_ion_edges(G):
    """
    Removes all ion edges from ion identity networking (used prior to network collapsing)
    :param G: networkx graph (MultiGraph)
    """
    remove_all_edges_of_type(G, CONST.EDGE.ION_TYPE)

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



def mark_all_node_types(G):
    """
    Marks all nodes as feature nodes or ion identity nodes (constants.NODE.TYPE_ATTRIBUTE)
    :param G: networkx graph (MultiGraph)
    """
    for node, data in G.nodes(data=True):
        if CONST.NODE.TYPE_ATTRIBUTE not in data:
            # ion identity node or feature node?
            if CONST.NODE.ION_NETWORK_ID_ATTRIBUTE in data:
                G.nodes[node][CONST.NODE.TYPE_ATTRIBUTE] = CONST.NODE.ION_TYPE
            else:
                G.nodes[node][CONST.NODE.TYPE_ATTRIBUTE] = CONST.NODE.FEATURE_TYPE

def equals_ignore_case(a, b):
    return str(a).lower().strip() == str(b).lower().strip()
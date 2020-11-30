#!/usr/bin/python
from networkx import nx
import logging_utils
import constants as CONST

logger = logging_utils.get_logger(__name__)


def collapse_ion_networks(G):
    """
    Collapse all ion identity networks. Does nothing if no ion identity networks are available.
    Does not change G, returns a copy.
    :param G: networkx graph (MultiGraph)
    :return: A copy of G with collapsed ion identity networks
    """
    H = G.copy()
    remove_all_ion_edges(H)
    # store all nodes of ion identity networks as: ion_network_id -> list of nodes
    ion_networks_dict = {}
    for node, attributes in H.nodes(data=True):
        # has ion identity network ID? Add to list of nodes to reconstruct IIN
        if CONST.NODE.ION_NETWORK_ATTRIBUTE in attributes:
            ion_network_id = attributes[CONST.NODE.ION_NETWORK_ATTRIBUTE]
            if ion_network_id is not None and len(str(ion_network_id).strip()) > 0:
                nodes = []
                if ion_network_id in ion_networks_dict:
                    nodes = ion_networks_dict[ion_network_id]
                    nodes.append(node)
                else:
                    nodes = [node]
                ion_networks_dict[ion_network_id] = nodes

    # sort by number of nodes in ion identity network
    sorted_ion_networks = sorted(ion_networks_dict.values(), key=lambda net: len(net), reverse=True)
    logger.info("Number of ion identity networks: "+str(len(sorted_ion_networks)))

    # merge all into the node with the highest abundance
    for network in sorted_ion_networks:
        if len(network) > 1:  # only collapse ion networks with >1 nodes
            sorted_nodes = sorted(network, key=lambda ion_node: H.nodes[ion_node][CONST.NODE.ABUNDANCE_ATTRIBUTE],
                                  reverse=True)
            merge_nodes(H, sorted_nodes)

    # TODO: Remove duplicate cosine edges (or other edges) between two nodes
    remove_duplicate_edges(H)

    # return copy of network G
    return H


def merge_nodes(G, nodes):
    """
    Merges all nodes into the first element of nodes, redirects the edges to this node and removes the other nodes
    from the graph.
    Only a few attributes are transferred.
    :param G: networkx graph (MultiGraph)
    :param nodes: sorted list of nodes to be merged (first remains - all other nodes are merged into the first node)
    """
    molecule_node = nodes[0]
    G.nodes[molecule_node][CONST.NODE.TYPE_ATTRIBUTE] = CONST.NODE.COLLAPSED_TYPE
    G.nodes[molecule_node][CONST.NODE.COLLAPSED_NODES_ATTRIBUTE] = len(nodes)
    # combine node attributed
    # intensity for each ion adduct
    sum_intensity = 0.0
    for node in nodes:
        if CONST.NODE.ADDUCT_ATTRIBUTE in G.nodes[node] and CONST.NODE.ABUNDANCE_ATTRIBUTE in G.nodes[node]:
            ion = G.nodes[node][CONST.NODE.ADDUCT_ATTRIBUTE]
            intensity = G.nodes[node][CONST.NODE.ABUNDANCE_ATTRIBUTE]
            G.nodes[molecule_node][ion + CONST.NODE.SPECIFIC_ION_ABUNDANCE] = intensity
            sum_intensity += intensity
        # TODO handle more attributes: How to add multiple library matches to this one node? Keep match with highest
        #  score?

    # add sum of ion intensities
    G.nodes[molecule_node][CONST.NODE.SUM_ION_INTENSITY_ATTRIBUTE] = sum_intensity

    # redirect all edges to the first node and remove nodes
    redirect_edges_and_delete_nodes(G, nodes[1:], molecule_node)


def redirect_edges_and_delete_nodes(G, nodes, target_node):
    """
    Redirect all edges to target_node and delete the list of nodes

    :param G: networkx graph (MultiGraph)
    :param nodes: list of nodes to be merged into target_node. Edges are redirect and nodes are deleted
    :param target_node: all edges are redirected to this node
    :return:
    """
    edges_to_add = []
    for n1, n2, key, data in G.edges(keys=True, data=True):
        if n1 is not target_node and n2 is not target_node:
            # For all edges related to one of the nodes to merge,
            # make an edge going to or coming from the new node
            try:
                if n1 in nodes:
                    edges_to_add.append((target_node, n2, key, data))

                elif n2 in nodes:
                    edges_to_add.append((n1, target_node, key, data))
            except:
                print("Error Adding Edge")
                continue
    # reconnect edges
    G.add_edges_from(edges_to_add)

    for n in nodes:  # remove the merged nodes
        if n is not target_node:
            G.remove_node(n)


def remove_duplicate_edges(G):
    """
    Remove duplicate edges between nodes after merging (edges of the same type)
    Keeps the highest score.
    :param G:
    :return:
    """
    #edges_to_remove = []
    #for n1 in G.nodes(data=True):
    #    for n2 in nx.neighbors(G, n1):

    #for n1, n2, key, data in G.edges(keys=True, data=True):
        # remove all edges with EDGE_TYPE_ATTRIBUTE = ION_EDGE_TYPE
    #    if EDGE_TYPE_ATTRIBUTE in data and str(data[EDGE_TYPE_ATTRIBUTE]).lower().strip() == ION_EDGE_TYPE:
    #        edges_to_remove.append((n1, n2, key))
    #G.remove_edges_from(edges_to_remove)

def remove_all_ion_edges(G):
    """
    Removes all edges from ion identity networking (used prior to network collapsing)
    :param G: networkx graph (MultiGraph)
    """
    EDGE_TYPE_ATTRIBUTE = CONST.EDGE.TYPE_ATTRIBUTE
    edges_to_remove = []
    for n1, n2, key, data in G.edges(keys=True, data=True):
        # remove all edges with EDGE_TYPE_ATTRIBUTE = ION_EDGE_TYPE
        if EDGE_TYPE_ATTRIBUTE in data and str(data[EDGE_TYPE_ATTRIBUTE]).lower().strip() == CONST.EDGE.ION_TYPE.lower():
            edges_to_remove.append((n1, n2, key))
    G.remove_edges_from(edges_to_remove)


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

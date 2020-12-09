#!/usr/bin/python


import os
import molecular_network_filtering_library
import ion_network_utils
import glob
import networkx as nx
import argparse
import logging_utils
import constants_network as CONST


def main():
    parser = argparse.ArgumentParser(description='Creating GraphML')
    parser.add_argument('input_pairs', help='input_pairs')
    parser.add_argument('input_clusterinfosummary', help='input_clusterinfosummary')
    parser.add_argument('input_librarysearch', help='input_librarysearch')
    parser.add_argument('output_graphml', help='output_graphml')
    parser.add_argument('--input_analoglibrarysearch', help='input_analoglibrarysearch')
    # options for ion identity molecular networking:
    # add "neutral molecule" nodes and collapse IIN edges
    # IIN edges = supplemental pairs (input_pairsfolder)
    parser.add_argument('--input_pairsfolder', help='input_pairsfolder')
    parser.add_argument('--collapse_ion_edges', default="False", help='collapse_ion_edges True or False')
    args = parser.parse_args()

    # export graphml to file
    collapse_ion_edges = args.collapse_ion_edges == "True" # Turning string to boolean
    create_graphml(args.input_pairs, args.input_clusterinfosummary, args.input_librarysearch,
                   args.input_analoglibrarysearch, args.input_pairsfolder, args.output_graphml,
                   collapse_ion_edges=collapse_ion_edges)

    
def create_graphml(input_pairs, input_clusterinfosummary, input_librarysearch, input_analoglibrarysearch,
                   input_pairsfolder, output_graphml, collapse_ion_edges=False):
    logger = logging_utils.get_logger(__name__)
    # Doing other filtering
    logger.debug("Creating network")
    G = molecular_network_filtering_library.loading_network(input_pairs, hasHeaders=True)
    molecular_network_filtering_library.add_clusterinfo_summary_to_graph(G, input_clusterinfosummary)
    molecular_network_filtering_library.add_library_search_results_to_graph(G, input_librarysearch)
    # mark all nodes as feature or ion identity nodes (constants.NODE.TYPE_ATTRIBUTE)
    logger.debug("Mark all node types")
    ion_network_utils.mark_all_node_types(G)

    # add analogs
    if input_analoglibrarysearch is not None:
        logger.debug("Add analog library search results")
        molecular_network_filtering_library.add_library_search_results_to_graph(G, input_analoglibrarysearch, annotation_prefix="Analog:")

    # add additional edges - e.g. ion identity edges between different ion species of the same molecule
    if input_pairsfolder is not None:
        all_pairs_files = glob.glob(os.path.join(input_pairsfolder, "*"))
        logger.debug("Adding additional edges from files: "+str(len(all_pairs_files)))
        for additional_pairs_file in all_pairs_files:
            logger.debug("Adding Additional Edges from " + str(additional_pairs_file))
            molecular_network_filtering_library.add_additional_edges(G, additional_pairs_file)

        # collapse all ion identity networks, each into a single node
        if collapse_ion_edges:
            logger.debug("Collapsing additional edges of type: " + CONST.EDGE.ION_TYPE)
            G = ion_network_utils.collapse_ion_networks(G)

    # export graphml
    logger.info("Writing graphml: "+output_graphml)
    nx.write_graphml(G, output_graphml, infer_numeric_types=True)

if __name__ == "__main__":
    main()

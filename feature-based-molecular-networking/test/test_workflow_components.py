import sys
import logging_utils
import numpy

sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
logger = logging_utils.get_logger(__name__)


def test_written_description():
    import write_description
    input_filename = "reference_data/params.xml"
    write_description.write_description(input_filename, "/dev/null")


def test_network_stats():
    import calculate_stats_graphml
    input_filename = "reference_data/network.graphml"
    calculate_stats_graphml.calculate_stats(input_filename, "/dev/null")


def test_metadata_test():
    import metadata_permanova_prioritizer

    input_filename = "reference_data/test_metadata_permanova_parse.tsv"
    selected_columns = metadata_permanova_prioritizer.permanova_validation(input_filename)

    print(selected_columns)


def test_additional_edges():
    import convert_networks_to_graphml
    import networkx as nx
    import ion_network_utils

    logger.debug("Exporting ion identity molecular network with ALL nodes (NO collapsing)")
    convert_networks_to_graphml.create_graphml("reference_data/IIN/edges.tsv",
                                               "reference_data/IIN/cluster_summary.tsv",
                                               "reference_data/IIN/library_matches.tsv",
                                               "reference_data/IIN/library_matches.tsv",
                                               "reference_data/IIN/additional_edges",
                                               "iin.graphml")

    logger.info("Reading graph")
    G = nx.read_graphml("iin.graphml")
    logger.info("Number of nodes in IIMN graph: " + str(len(G.nodes())))
    logger.info("Number of edges in IIMN graph: " + str(len(G.edges())))

    # access cosine similarity edge from molecular networking
    for a, b, data in G.edges(data=True):
        if (a == '7347' or b == '7347') and (a == '9043' or b == '9043'):
            logger.info(data)
    listy = G.get_edge_data('7347', '9043', key=ion_network_utils.COSINE_EDGE_TYPE)
    logger.info("edge info:" + str(listy))
    mass_difference = float(listy[0]["mass_difference"])
    mass_difference = round(mass_difference, 4)
    # safely compare floating point numbers
    assert (numpy.isclose(mass_difference, 3.0051))


def test_collapse_ion_identity_networks():
    import convert_networks_to_graphml
    import networkx as nx

    logger.info("Exporting ion identity molecular network with collapsed nodes")
    convert_networks_to_graphml.create_graphml("reference_data/IIN/edges.tsv",
                                               "reference_data/IIN/cluster_summary.tsv",
                                               "reference_data/IIN/library_matches.tsv",
                                               "reference_data/IIN/library_matches.tsv",
                                               "reference_data/IIN/additional_edges",
                                               "iin.graphml", True)

    logger.info("Reading graph")
    G = nx.read_graphml("iin.graphml")
    logger.info("Number of nodes in collapsed IIMN graph: " + str(len(G.nodes())))
    logger.info("Number of edges in collapsed IIMN graph: " + str(len(G.edges())))
    # TODO: add test values
    assert (len(G.nodes()) < 1140)


def test_clustersummary():
    import clusterinfosummary_for_featurenetworks

    input_param_xml = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/params.xml"
    input_consensus_feature_file = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/quant.csv"
    metadata_files = ["reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/metadata_table-00000.txt"]
    input_mgf_filename = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/spec-00000.mgf"
    output_clusterinfo_summary = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/clustersummary.tsv"

    clusterinfosummary_for_featurenetworks.process(input_param_xml, input_consensus_feature_file, metadata_files,
                                                   input_mgf_filename, output_clusterinfo_summary)


def test_permanova_selection():
    import metadata_permanova_prioritizer

    permanova_colums = metadata_permanova_prioritizer.permanova_validation(
        "reference_data/permanova/metadata_table-00000.txt")
    assert (len(permanova_colums) == 4)

    permanova_colums = metadata_permanova_prioritizer.permanova_validation(
        "reference_data/permanova/kelly_metadata.txt")
    print(permanova_colums)
    assert ("ATTRIBUTE_bdi_group" in permanova_colums)

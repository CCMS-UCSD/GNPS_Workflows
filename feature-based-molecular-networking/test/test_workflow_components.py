import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")


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

    convert_networks_to_graphml.create_graphml("reference_data/IIN/edges.tsv", 
    "reference_data/IIN/cluster_summary.tsv", 
    "reference_data/IIN/library_matches.tsv", 
    "reference_data/IIN/library_matches.tsv", 
    "reference_data/IIN/additional_edges", 
    "iin.graphml")


def test_clustersummary():
    import clusterinfosummary_for_featurenetworks

    input_param_xml = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/params.xml"
    input_consensus_feature_file = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/quant.csv"
    metadata_files = ["reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/metadata_table-00000.txt"]
    input_mgf_filename = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/spec-00000.mgf"
    output_clusterinfo_summary = "reference_data/clustersummary/bd57fce66c81488cbf13fa4d0e19d88f/clustersummary.tsv"

    clusterinfosummary_for_featurenetworks.process(input_param_xml, input_consensus_feature_file, metadata_files, input_mgf_filename, output_clusterinfo_summary)

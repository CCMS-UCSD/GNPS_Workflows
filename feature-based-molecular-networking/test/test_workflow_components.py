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
    import networkx as nx
    import unittest

    convert_networks_to_graphml.create_graphml("reference_data/IIN/edges.tsv", 
    "reference_data/IIN/cluster_summary.tsv", 
    "reference_data/IIN/library_matches.tsv", 
    "reference_data/IIN/library_matches.tsv", 
    "reference_data/IIN/additional_edges", 
    "iin.graphml")
    
    G = nx.read_graphml("iin.graphml")   
    listy = G.get_edge_data('7347','9043')
    mass_difference = float(listy[0]["mass_difference"])
    mass_difference = round(mass_difference, 4)
    if  3.0051 == mass_difference: 
        return(0)
    else:
        return(1)

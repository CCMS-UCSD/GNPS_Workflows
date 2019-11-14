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

import sys
sys.path.insert(0, "../tools/molecularsearch-gc/")


def test():
    import filter_gc_identifications
    input_filename = "reference_data/filtering/full_results.tsv"
    output_filename = "filtered_results.tsv"
    filter_gc_identifications.filter_identifications(input_filename, output_filename)

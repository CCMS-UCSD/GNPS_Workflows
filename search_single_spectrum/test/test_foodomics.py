import pandas as pd

import sys
sys.path.insert(0, "../tools/search_single_spectrum/")

import foodomics_track

def test():
    input_filename = "data/foodomics/all_dataset_matchs.tsv"

    matches_df = pd.read_csv(input_filename, sep="\t")
    metadata_df = pd.read_csv("../tools/search_single_spectrum/gfop_ontology_foodmasst.txt", sep="\t")
    test_output = pd.read_csv("data/foodomics/foodmasst_test_output.tsv", sep="\t")

    enrichment_df = foodomics_track.calculate_enrichment(matches_df, metadata_df)

    pd.testing.assert_frame_equal(test_output, enrichment_df)

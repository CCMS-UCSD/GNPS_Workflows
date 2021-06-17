import pandas as pd
import unittest
import sys
sys.path.insert(0, "../tools/search_single_spectrum/")
sys.path.insert(0, "tools/search_single_spectrum/")
import foodomics_track


class TestLoaders(unittest.TestCase):
    def test(self):
        input_filename = "data/foodomics/all_dataset_matchs.tsv"
        foodomics_metadata = "../tools/search_single_spectrum/gfop_ontology_foodmasst.txt"

        out_foodmasst = "tmp/out_foodmasst.tsv"
        out_filtered_food_metadata = "tmp/out_filtered_food_metadata.tsv"

        # run
        foodomics_track.combine_food_masst(foodomics_metadata, input_filename, out_foodmasst, out_filtered_food_metadata)

        # ground truth test file
        test_output = pd.read_csv("data/foodomics/foodmasst_test_output.tsv", sep="\t")
        test_matches_filtered = pd.read_csv("data/foodomics/filtered_food_metadata.tsv", sep="\t")

        # read back results from tmp files
        enrichment_df = pd.read_csv(out_foodmasst, sep="\t")
        matches_filtered = pd.read_csv(out_filtered_food_metadata, sep="\t")

        # actual test - ignore sorting
        pd.testing.assert_frame_equal(test_matches_filtered, matches_filtered, check_like=True)
        pd.testing.assert_frame_equal(test_output, enrichment_df, check_like=True)


if __name__ == '__main__':
    unittest.main()
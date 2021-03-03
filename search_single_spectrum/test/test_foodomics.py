import pandas as pd

import sys
sys.path.insert(0, "../tools/search_single_spectrum/")

import foodomics_track

def test():
    input_filename = "data/foodomics/all_dataset_matchs.tsv"

    matches_df = pd.read_csv(input_filename, sep="\t")
    metadata_df = pd.read_csv("../tools/search_single_spectrum/11442_foodomics_multiproject_metadata_20200630_submission.txt", sep="\t")

    enrichment_df = foodomics_track.calculate_enrichment(matches_df, metadata_df)

    print(enrichment_df)


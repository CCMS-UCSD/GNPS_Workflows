# this module takes in searches for one clustered scan and runs searches against the current version of the foodomics library. A tsv containing the predicted types of the clustered scan spectrum, confidence and product scores and number of hits would be returned.

# current version of the search maximizes sensitvity by lowering the product score threshold to 1 and the confidence to 0.3 so that it's most likely to reveal the top one to top three candidate types of the molecule at different detail level on the food tree.

import sys
import pandas as pd
import os
import argparse

def calculate_enrichment(file_occurrent_df, metadata_df):
    # Removing extensions on both
    file_occurrent_df["basefilename"] = file_occurrent_df["basefilename"].apply(lambda x: os.path.splitext(x)[0])
    metadata_df["filename"] = metadata_df["filename"].apply(lambda x: os.path.splitext(x)[0])

    # Filter to approrpaite dataset
    file_occurrent_df = file_occurrent_df[file_occurrent_df["dataset_id"] == "MSV000084900"]

    columns_to_consider = ["ontology_term"]

    output_list = []

    # Lets go through columns
    for metadata_column in columns_to_consider:
        all_unique_values = set(metadata_df[metadata_column])
        for group_value in all_unique_values:
            group_df = metadata_df[metadata_df[metadata_column] == group_value]

            total_group_size = len(group_df)

            merged_df = file_occurrent_df.merge(group_df, how="inner", left_on="basefilename", right_on="filename")
            matched_size = len(merged_df)

            if total_group_size == 0:
                occurrence_fraction = 0
            else:
                occurrence_fraction = float(matched_size) / float(total_group_size)

            output_dict = {}
            output_dict["occurrence_fraction"] = occurrence_fraction
            output_dict["metadata_column"] = metadata_column
            output_dict["group_value"] = group_value
            output_dict["group_size"] = total_group_size
            output_dict["matched_size"] = matched_size

            output_list.append(output_dict)

    return pd.DataFrame(output_list)

def metadata_file_matches(file_occurrent_df):
    # Filter to appropriate dataset
    file_occurrent_df = file_occurrent_df[file_occurrent_df["dataset_id"] == "MSV000084900"]

    # Get foodomics full metadata
    gfop_meta = pd.read_csv('https://raw.githubusercontent.com/ka-west/GFOPontology/master/data/foodomics_metadata_08APR21.txt', sep='\t')

    # Removing extensions on both
    file_occurrent_df["basefilename"] = file_occurrent_df["basefilename"].apply(lambda x: os.path.splitext(x)[0])
    gfop_meta["filename"] = gfop_meta["filename"].apply(lambda x: os.path.splitext(x)[0])

    # Return metadata for matching files
    return(gfop_meta[gfop_meta.filename.isin(file_occurrent_df["basefilename"])])

def main():
    parser = argparse.ArgumentParser(description='Create foodomics enrichment')
    parser.add_argument('foodomics_metadata', help='foodomics_metadata')
    parser.add_argument('matches_results', help='matches_results')
    parser.add_argument('output_enrichment', help='output_enrichment')
    parser.add_argument('metadata_matches', help='metadata_matches')
    args = parser.parse_args()

    try:
        matches_df = pd.read_csv(args.matches_results, sep="\t")
        metadata_df = pd.read_csv(args.foodomics_metadata, sep="\t")
        enrichment_df = calculate_enrichment(matches_df, metadata_df)
        enrichment_df.to_csv(args.output_enrichment, sep="\t", index=False)
        matched_metadata = metadata_file_matches(matches_df)
        matched_metadata.to_csv(args.metadata_matches, sep="\t", index=False)
    except:
        with open(args.output_enrichment, "w") as o:
            o.write("EMPTY")

if __name__ == "__main__":
    main()

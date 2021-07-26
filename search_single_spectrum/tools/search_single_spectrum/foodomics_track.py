# this module takes in searches for one clustered scan and runs searches against the current version of the foodomics
# library. A tsv containing the predicted types of the clustered scan spectrum, confidence and product scores and
# number of hits would be returned.

# current version of the search maximizes sensitvity by lowering the product score threshold to 1 and the confidence
# to 0.3 so that it's most likely to reveal the top one to top three candidate types of the molecule at different
# detail level on the food tree.

import sys
import pandas as pd
import os
import argparse


def calculate_enrichment(matches_df, metadata_df):
    # Removing extensions on both
    metadata_df["filename"] = metadata_df["filename"].apply(lambda x: os.path.splitext(x)[0])

    columns_to_consider = ["ontology_term"]

    output_list = []

    # Lets go through columns
    for metadata_column in columns_to_consider:
        all_unique_values = set(metadata_df[metadata_column])
        for group_value in all_unique_values:
            group_df = metadata_df[metadata_df[metadata_column] == group_value]

            total_group_size = len(group_df)

            merged_df = matches_df.merge(group_df, how="inner", left_on="basefilename", right_on="filename")
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


def metadata_file_matches(matches_df):
    """
    Create filtered metadata table for MASST matched files
    :param matches_df: filtered MASST matches in GFOP files : pandas dataframe
    :return: filtered metadata
    """

    # Get foodomics full metadata
    # gfop_meta = pd.read_csv('https://raw.githubusercontent.com/ka-west/GFOPontology/master/data
    # /foodomics_metadata_foodmasst.txt', sep='\t')
    # gfop_meta = pd.read_csv(
    #     'https://github.com/global-foodomics/GFOPontology/raw/master/data/foodomics_metadata_foodmasst.tsv', sep='\t')
    gfop_meta = pd.read_csv('foodomics_metadata_foodmasst.tsv', sep='\t')

    # Removing extensions on both
    gfop_meta["filename"] = gfop_meta["filename"].apply(lambda x: os.path.splitext(x)[0])

    # Return metadata for matching files
    return (gfop_meta[gfop_meta.filename.isin(matches_df["basefilename"])])


def filter_matches(matches_df):
    """
    Filter a pandas data frame with MASST matches to only those from the global foodomics dataset
    :param matches_df: MASST matches
    :return: filtered pandas data frame
    """
    matches_df["basefilename"] = matches_df["basefilename"].apply(lambda x: os.path.splitext(x)[0])
    # Filter to approrpaite dataset
    return matches_df[matches_df["dataset_id"] == "MSV000084900"]


def combine_food_masst(foodomics_metadata, matches_results, output_enrichment, output_metadata_matches):
    try:
        matches_df = pd.read_csv(matches_results, sep="\t")
        # filter to global foodomics
        matches_df = filter_matches(matches_df)

        metadata_df = pd.read_csv(foodomics_metadata, sep="\t")
        enrichment_df = calculate_enrichment(matches_df, metadata_df)
        if output_enrichment is not None:
            # sort and save
            sorted_df = enrichment_df.sort_values(by=["group_value"])
            sorted_df.to_csv(output_enrichment, sep="\t", index=False)

        matched_metadata = metadata_file_matches(matches_df)
        if output_metadata_matches is not None:
            matched_metadata.to_csv(output_metadata_matches, sep="\t", index=False)

        return enrichment_df, matched_metadata
    except:
        # on error write all files as empty
        with open(output_enrichment, "w") as o:
            pass
            # o.write("")
        with open(output_metadata_matches, "w") as o:
            pass
            # o.write("")


def main():
    parser = argparse.ArgumentParser(description='Create foodomics enrichment')
    parser.add_argument('foodomics_metadata', help='the foodomics metadata table')
    parser.add_argument('matches_results', help='MASST match results')
    parser.add_argument('output_enrichment', help='Output tsv file for enrichment results')
    parser.add_argument('metadata_matches', help='Output filtered metadata tsv file')
    args = parser.parse_args()

    combine_food_masst(args.foodomics_metadata, args.matches_results, args.output_enrichment, args.metadata_matches)


if __name__ == "__main__":
    main()

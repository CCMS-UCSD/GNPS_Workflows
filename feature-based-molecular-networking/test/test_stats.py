import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import calculate_stats
import os
import pandas as pd


def test_no_column():
    try:
        os.mkdir("output_plots")
    except:
        pass
    try:
        os.mkdir("output_summary")
    except:
        pass

    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", 
                                        "reference_stats/metadata.tsv", 
                                        None,
                                        "output_summary", 
                                        output_plots_folder="output_plots")

def test_no_column_library():
    try:
        os.mkdir("output_plots")
    except:
        pass
    try:
        os.mkdir("output_summary_library")
    except:
        pass

    libraryidentifications_df = pd.read_csv("reference_stats/librarysearch.tsv", sep=None, error_bad_lines=False)
    libraryidentifications_df = libraryidentifications_df[["#Scan#", "Compound_Name", "Smiles", "INCHI"]]
    libraryidentifications_df = libraryidentifications_df.rename(columns={"Compound_Name":"featurecompoundname", "Smiles":"featuresmiles", "INCHI":"featureinchi"})

    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", 
                                        "reference_stats/metadata.tsv", 
                                        None,
                                        "output_summary_library", 
                                        output_plots_folder="output_plots",
                                        libraryidentifications_df=libraryidentifications_df)

def test_column():
    try:
        os.mkdir("output_plots_chosen")
    except:
        pass
    try:
        os.mkdir("output_summary")
    except:
        pass

    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", 
                                        "reference_stats/metadata.tsv", 
                                        None,
                                        "output_summary", 
                                        output_plots_folder="output_plots_chosen",
                                        metadata_column="ATTRIBUTE_sample_type",
                                        condition_first="urine",
                                        condition_second="unknown")

def test_facet_column():
    try:
        os.mkdir("output_plots_facet")
    except:
        pass
    try:
        os.mkdir("output_summary")
    except:
        pass

    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", 
                                        "reference_stats/metadata.tsv", 
                                        None,
                                        "output_summary", 
                                        output_plots_folder="output_plots_facet",
                                        metadata_column="ATTRIBUTE_sex",
                                        condition_first="male",
                                        condition_second="female",
                                        metadata_facet_column="ATTRIBUTE_disease_stage")
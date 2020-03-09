import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import calculate_stats
import os

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
                                        "output_summary", 
                                        output_plots_folder="output_plots")

def test_column():
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
                                        "output_summary", 
                                        output_plots_folder="output_plots",
                                        metadata_column="ATTRIBUTE_sample_type",
                                        condition_first="urine",
                                        condition_second="unknown")
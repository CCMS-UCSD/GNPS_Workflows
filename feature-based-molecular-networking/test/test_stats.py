import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import calculate_stats
import os

def test():
    try:
        os.mkdir("output_plots")
    except:
        pass
    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", "reference_stats/metadata.tsv", output_plots_folder="output_plots")
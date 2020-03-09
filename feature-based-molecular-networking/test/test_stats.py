import sys
sys.path.insert(0, "../tools/feature-based-molecular-networking/scripts/")
import calculate_stats

def test():
    calculate_stats.calculate_statistics("reference_stats/feature_table.csv", "reference_stats/metadata.tsv")
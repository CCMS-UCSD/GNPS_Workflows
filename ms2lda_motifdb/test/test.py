import sys
sys.path.insert(0, "../tools/ms2lda_motifdb")

def test_graphml_output():
    import create_graphml

    create_graphml.create_graphml("reference_data/ms2lda_1/output_results/output_motifs_in_scans.tsv",
    "reference_data/ms2lda_1/output_pairs/pairs.tsv",
    "output.graphml", "output.pairs")
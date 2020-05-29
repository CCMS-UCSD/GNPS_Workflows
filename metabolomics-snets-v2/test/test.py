import sys
sys.path.insert(0, "../tools/metabolomicsnetsv2/scripts/")

def test_library_enrichment():
    import getGNPS_library_annotations
    getGNPS_library_annotations.enrich_output("./test_data/raw_search_results.tsv", "./results_db.tsv")
    
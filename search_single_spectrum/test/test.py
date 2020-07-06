import sys

sys.path.insert(0, "../tools/search_single_spectrum")

def test():
    import xic_masst
    new_record_df = xic_masst.process_masst_xic("test_data/SEARCH_SINGLE_SPECTRUM-7e961554-view_all_spectra_datasets_matched-main.tsv")

    print(new_record_df)
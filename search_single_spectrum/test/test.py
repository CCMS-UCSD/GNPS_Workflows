import pandas as pd

import sys
sys.path.insert(0, "../tools/search_single_spectrum/")

import masst_network


def test():
    import requests_cache
    requests_cache.install_cache('demo_cache')
    MASST_TASK = "c6b2797224f34d819d20dd7af622bc6b"

    # Loading MASST information
    spectra_matches_df = pd.read_csv("https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file=all_dataset_spectra_matches/&block=main".format(MASST_TASK), sep="\t")

    masst_network.create_masst_network(spectra_matches_df, "test.graphml")
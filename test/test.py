import requests
import os
import sys
import pandas as pd
sys.path.insert(0, "../shared_code")
import molecular_network_filtering_library
import networkx as nx

def test_network_topology():
    print("test topology")

    # Getting pairs data
    pairs_filename = "pairs.tsv"
    if not os.path.exists(pairs_filename):
        pairs_data_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=b8b5f2f0581c46f1b61ce047d3bbad16&block=main&file=pairs/pairs.tsv"
        os.system('wget "{}" -O pairs.tsv'.format(pairs_data_url))

        pairs_df = pd.read_csv(pairs_filename, sep="\t", nrows=10000)
        pairs_df.to_csv(pairs_filename, sep="\t", index=False)

    G = molecular_network_filtering_library.loading_network(pairs_filename, hasHeaders=True, edgetype="Spec2Vec")
    molecular_network_filtering_library.filter_top_k(G, 10)
    molecular_network_filtering_library.filter_component_additive(G, 100)
    nx.write_graphml(G, "additive.graphml")
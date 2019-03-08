import os
import sys
from pyMolNetEnhancer import *
import pandas as pd

input_folder = sys.argv[1]
output_folder = sys.argv[2]

edges = pd.read_csv(os.path.join(input_folder, "output_ms2lda_edges.tsv"), sep = '\t')
nodes = pd.read_csv(os.path.join(input_folder, "output_ms2lda_nodes.tsv"), sep = '\t')

motif_graph = make_motif_graphml(nodes, edges)

output_graphml_filename = os.path.join(output_folder, "ms2lda_network.graphml")
nx.write_graphml(motif_graph, output_graphml_filename, infer_numeric_types = True)

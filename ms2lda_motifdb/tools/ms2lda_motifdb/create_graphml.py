import os
import sys
from pyMolNetEnhancer import *
import pandas as pd
import networkx as nx
import argparse

parser = argparse.ArgumentParser(description='Creates MS2LDA')
parser.add_argument('ms2lda_results', help='ms2lda_results')
parser.add_argument('input_network_edges', help='input_network_edges')
parser.add_argument('output_folder', help='output_folder')
parser.add_argument('input_network_overlap', type=float, help='input_network_overlap')
parser.add_argument('input_network_pvalue', type=float, help='input_network_pvalue')
parser.add_argument('input_network_topx', type=int, help='input_network_topx')

args = parser.parse_args()

edges = pd.read_csv(args.input_network_edges, sep="\t")
motifs = pd.read_csv(os.path.join(args.ms2lda_results, "output_ms2lda_nodes.tsv"), sep = '\t')
#motifs["scans"] = motifs["scan"]

print(edges.keys())
print(motifs.keys())

motif_network = Mass2Motif_2_Network(edges, motifs, prob = 0.01, overlap = 0.3, top = 5)
MG = make_motif_graphml(motif_network['nodes'],motif_network['edges'])

# edges = pd.read_csv(os.path.join(input_folder, "output_ms2lda_edges.tsv"), sep = '\t')
# edges["shared_motifs"] = edges["SharedMotifs"]
# edges["TopSharedMotifs"] = edges["topX"]
#
# edges = edges.drop(columns=['topX', 'SharedMotifs'])
#
# nodes = pd.read_csv(os.path.join(input_folder, "output_ms2lda_nodes.tsv"), sep = '\t')
# nodes["precursormass"] = nodes["precursor.mass"]
# nodes["parentrt"] = nodes["retention.time"]
#
# nodes = nodes.drop(columns=['precursor.mass', 'retention.time'])
#
# """Dropping other Columns"""
# whitelisted_headers = ["precursormass", "parentrt", "scans", "document", "motif", "overlap", "probability", "document.annotation"]
# #nodes = nodes[whitelisted_headers]
#
# motif_graph = make_motif_graphml(nodes, edges)

output_graphml_filename = os.path.join(args.output_folder, "ms2lda_network.graphml")
nx.write_graphml(MG, output_graphml_filename, infer_numeric_types = True)

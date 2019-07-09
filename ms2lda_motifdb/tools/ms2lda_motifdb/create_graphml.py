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

try:

    # prepare data
    motifs = pd.read_csv(os.path.join(args.ms2lda_results, "output_motifs_in_scans.tsv"), sep = '\t')
    motifs = motifs.rename(columns={'scan': 'scans'})
    motifs = motifs.rename(columns={'precursor.mass': 'precursormass'})
    motifs = motifs.rename(columns={'retention.time': 'parentrt'})
    motifs['document'] = motifs['scans']
    #motifs = motifs[['scans','precursormass','parentrt','document','motif','probability','overlap']]
    motifs = motifs[['scans','precursormass','parentrt','document','motif','probability','overlap','motifdb_url', 'motifdb_annotation']]


    edges = pd.read_csv(args.input_network_edges, sep="\t")
    edges = edges[["CLUSTERID1", "CLUSTERID2", "DeltaMZ", "MEH", "Cosine", "OtherScore", "ComponentIndex"]]

    # run pyMolNetEnhancer

    motif_network = Mass2Motif_2_Network(edges, motifs, prob = args.input_network_pvalue, overlap = args.input_network_overlap, top = args.input_network_topx)
    motif_network['nodes']['motifdb_url'] = motif_network['nodes']['motifdb_url'].agg(lambda x: ','.join(map(str, x)))
    motif_network['nodes']['motifdb_annotation'] = motif_network['nodes']['motifdb_annotation'].agg(lambda x: ','.join(map(str, x)))

    # create graphml file

    MG = make_motif_graphml(motif_network['nodes'],motif_network['edges'])
    output_graphml_filename = os.path.join(args.output_folder, "ms2lda_network.graphml")
    nx.write_graphml(MG, output_graphml_filename, infer_numeric_types = True)
except:
    print("Error in Creating Graphml")


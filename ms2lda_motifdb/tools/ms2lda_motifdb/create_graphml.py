import os
import sys
from pyMolNetEnhancer import *

input_folder = sys.argv[1]
output_folder = sys.argv[2]

edges = pd.read_csv(os.path.join(input_folder, "")), sep = '\t')

motif_graph = make_motif_graphml(motif_network['nodes'],motif_network['edges'])


output_graphml_filename = os.path.join(output_folder, "ms2lda_network.graphml")

with open(output_graphml_filename, "w") as output_file:
    output_file.write("DONE")

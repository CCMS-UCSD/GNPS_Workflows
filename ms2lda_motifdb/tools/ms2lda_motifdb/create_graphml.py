import os
import sys

input_folder = sys.argv[1]
output_folder = sys.argv[2]

output_graphml_filename = os.path.join(output_folder, "ms2lda_network.graphml")

with open(output_graphml_filename, "w") as output_file:
    output_file.write("DONE")

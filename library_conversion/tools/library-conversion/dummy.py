import sys

output_filename = sys.argv[1]

with open(output_filename, "w") as output_file:
    output_file.write("header\ndata")
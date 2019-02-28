#!/usr/bin/python


import sys
import getopt
import os
import json

def usage():
    print "<output parameters files> <parallelism>"

def main():
    print sys.argv

    output_parameters_folder = sys.argv[1]
    partition_count = int(sys.argv[2])

    #Creating a command line for each partition
    for i in range(partition_count):
        output_param_filename = os.path.join(output_parameters_folder, str(i) + ".json")
        output_map = {}
        output_map["total_paritions"] = partition_count
        output_map["node_partition"] = i
        open(output_param_filename, "w").write(json.dumps(output_map))

    exit(0)


if __name__ == "__main__":
    main()

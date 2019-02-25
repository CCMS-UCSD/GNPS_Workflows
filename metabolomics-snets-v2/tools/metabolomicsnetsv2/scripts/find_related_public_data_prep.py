#!/usr/bin/python


import sys
import getopt
import os
import math
import json
import ming_proteosafe_library
import ming_gnps_library

def usage():
    print("<param.xml> <output folder> <parallelism level>")



def main():
    paramxml_input_filename = sys.argv[1]
    output_json_folder = sys.argv[2]
    parallelism = int(sys.argv[3])

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    try:
       if params_obj["FIND_MATCHES_IN_PUBLIC_DATA"][0] != "1":
           parallelism = 1
    except:
       parallelism = 1

    #dataset_dict = ming_proteosafe_library.get_all_dataset_dict()
    all_datasets = []
    try:
        all_datasets = ming_gnps_library.get_all_datasets()
    except:
        all_datasets = []

    for i in range(parallelism):
        output_map = {"node_partition" : i, "total_paritions" : parallelism}
        partitioned_datasets = all_datasets[i::parallelism]
        output_map["all_datasets"] = partitioned_datasets

        dataset_map = {}
        for dataset in partitioned_datasets:
            dataset_map[dataset["dataset"]] = dataset

        output_map["dataset_dict"] = dataset_map
        output_filename = os.path.join(output_json_folder, str(i) + ".json")
        open(output_filename, "w").write(json.dumps(output_map))



if __name__ == "__main__":
    main()

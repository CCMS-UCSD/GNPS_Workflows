#!/usr/bin/python


import sys
import getopt
import os
import math
import json
import ming_proteosafe_library

def usage():
    print "<param.xml> <output folder> <parallelism level>"



def main():
    paramxml_input_filename = sys.argv[1]
    output_json_folder = sys.argv[2]
    parallelism = int(sys.argv[3])

    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    try:
       if params_obj["MATCH_REFERENCE_DATASETS"][0] != "1":
           parallelism = 1
    except:
       parallelism = 1
    all_datasets = []
    try:
        temp_datasets = ming_proteosafe_library.get_all_datasets()

        #Filtering datasets to reference datasets
        for dataset in temp_datasets:
            if dataset["title"].find("GNPS_ref_") != -1:
                all_datasets.append(dataset)

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

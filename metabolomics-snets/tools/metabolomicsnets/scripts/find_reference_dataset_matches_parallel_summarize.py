#!/usr/bin/python


import sys
import getopt
import os
import math
import json
import ming_proteosafe_library
import ming_fileio_library
from collections import defaultdict

def usage():
    print "<paramxml> <all matches> <summary>"



def main():
    paramxml_input_filename = sys.argv[1]
    all_matches_filename = sys.argv[2]
    summary_filename = sys.argv[3]


    params_obj = ming_proteosafe_library.parse_xml_file(open(paramxml_input_filename))

    try:
       if params_obj["MATCH_REFERENCE_DATASETS"][0] != "1":
           output_dict = {}
           ming_fileio_library.write_dictionary_table_data(output_dict, summary_filename)
           exit(0)
    except:
       output_dict = {}
       ming_fileio_library.write_dictionary_table_data(output_dict, summary_filename)
       exit(0)
    dataset_dict = []
    try:
        dataset_dict = ming_proteosafe_library.get_all_dataset_dict()
    except:
        dataset_dict = {}

    row_count, table_data = ming_fileio_library.parse_table_with_headers(all_matches_filename)

    matches_list = []
    for i in range(row_count):
        match = {}
        for key in table_data:
            match[key] = table_data[key][i]
        matches_list.append(match)

    matches_by_scan = defaultdict(list)
    for match in matches_list:
        query_spectrum_key = match["query_filename"] + ":" + match["query_scan"]

        matches_by_scan[query_spectrum_key].append(match)


    output_dict = defaultdict(list)
    for spectrum_key in matches_by_scan:
        contains_blank = 0
        datasets_contained = []
        compound_identifications = []
        spectrum_ids = []
        all_scores = []
        for match in matches_by_scan[spectrum_key]:
            if match["is_blank"] == "1":
                contains_blank = 1
            datasets_contained.append(match["dataset_id"])
            compound_identifications.append(match["identification"])
            spectrum_ids.append(match["spectrum_id"])
            all_scores.append(match["score"])
        datasets_contained = list(set(datasets_contained))
        compound_identifications = list(set(compound_identifications))
        spectrum_ids = list(set(spectrum_ids))
        dataset_descriptions = []

        for dataset_id in datasets_contained:
            dataset_descriptions.append(dataset_dict[dataset_id]["title"].strip())




        output_dict["query_scan"].append(matches_by_scan[spectrum_key][0]["query_scan"])
        output_dict["query_filename"].append(matches_by_scan[spectrum_key][0]["query_filename"])
        output_dict["dataset_list"].append("!".join(datasets_contained))
        output_dict["dataset_descriptions"].append("!".join(dataset_descriptions))
        output_dict["contains_blank"].append(contains_blank)
        output_dict["identification"].append("!".join(compound_identifications))
        output_dict["spectrum_id"].append("!".join(spectrum_ids))
        output_dict["best_score"].append(max(all_scores))




    for key in output_dict:
        print(key, len(output_dict[key]))

    ming_fileio_library.write_dictionary_table_data(output_dict, summary_filename)









if __name__ == "__main__":
    main()

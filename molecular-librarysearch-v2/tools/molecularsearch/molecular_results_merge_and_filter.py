#!/usr/bin/python


import sys
import getopt
import os
import ming_fileio_library
import ming_proteosafe_library
from collections import defaultdict

def usage():
    print("<input folder> <param.xml> <output tsv file>")

def main():
    input_folder_path = sys.argv[1]
    param_xml_filename = sys.argv[2]
    output_tsv = sys.argv[3]

    files = ming_fileio_library.list_files_in_dir(input_folder_path)
    params_obj = ming_proteosafe_library.parse_xml_file(open(param_xml_filename))

    top_k = 1
    try:
        top_k = int(params_obj["TOP_K_RESULTS"][0])
    except:
        top_k = 1

    #merged_dict = defaultdict(list)
    merged_results = []

    for input_file in files:
        print("loading", input_file)
        row_count, table_data = ming_fileio_library.parse_table_with_headers(input_file)
        for i in range(row_count):
            result_dict = {}
            for key in table_data:
                result_dict[key] = table_data[key][i]
            merged_results.append(result_dict)


    results_per_spectrum = defaultdict(list)

    for result_obj in merged_results:
        spectrum_unique_key = result_obj["SpectrumFile"] + "___" + result_obj["#Scan#"]

        results_per_spectrum[spectrum_unique_key].append(result_obj)

    output_results = []
    for spectrum_unique_key in results_per_spectrum:
        sorted_results = sorted(results_per_spectrum[spectrum_unique_key], key=lambda spectrum_obj: float(spectrum_obj["MQScore"]), reverse=True)
        filtered_results = sorted_results[:top_k]
        output_results += filtered_results

    output_dict = defaultdict(list)

    for result_obj in output_results:
        for key in result_obj:
            output_dict[key].append(result_obj[key])


    ming_fileio_library.write_dictionary_table_data(output_dict, output_tsv)

if __name__ == "__main__":
    main()

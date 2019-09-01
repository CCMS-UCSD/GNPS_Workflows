#!/usr/bin/python


import sys
import getopt
import os
import ming_fileio_library
import statistics
from collections import defaultdict

def usage():
    print("<input file> <output tsv file>")

def main():
    input_filename = sys.argv[1]
    output_tsv = sys.argv[2]

    results_list = ming_fileio_library.parse_table_with_headers_object_list(input_filename)
    results_by_compound_name = defaultdict(list)
    for result in results_list:
        annotation_string = result["Compound_Name"]
        results_by_compound_name[annotation_string].append(result)


    output_results = []
    for compound_name in results_by_compound_name:
        best_result = sorted(results_by_compound_name[compound_name], key=lambda result: float(result["MQScore"]), reverse=True)[0]

        all_RTs = [float(result["RT_Query"]) for result in results_by_compound_name[compound_name]]
        all_MZs = [float(result["SpecMZ"]) for result in results_by_compound_name[compound_name]]
        all_MZ_ppmerror = [float(result["MZErrorPPM"]) for result in results_by_compound_name[compound_name]]

        rt_mean = statistics.mean(all_RTs)
        rt_median = statistics.median(all_RTs)
        mz_mean = statistics.mean(all_MZs)
        mz_ppm_mean = statistics.mean(all_MZ_ppmerror)

        rt_max = max(all_RTs)
        rt_min = min(all_RTs)

        mz_max = max(all_MZs)
        mz_min = min(all_MZs)

        #STDDev
        rt_stdev = 0.0
        mz_stdev = 0.0
        ppmerror_stdev = 0.0
        if len(all_RTs) > 1:
            rt_stdev = statistics.stdev(all_RTs)
            mz_stdev = statistics.stdev(all_MZs)
            ppmerror_stdev = statistics.stdev(all_MZ_ppmerror)

        best_result["rt_mean"] = rt_mean
        best_result["rt_median"] = rt_median
        best_result["mz_mean"] = mz_mean
        best_result["mz_ppm_mean"] = mz_ppm_mean
        best_result["rt_max"] = rt_max
        best_result["rt_min"] = rt_min
        best_result["mz_max"] = mz_max
        best_result["mz_min"] = mz_min
        best_result["rt_stdev"] = rt_stdev
        best_result["mz_stdev"] = mz_stdev
        best_result["ppmerror_stdev"] = ppmerror_stdev
        best_result["number_spectra"] = len(all_RTs)

        output_results.append(best_result)

    ming_fileio_library.write_list_dict_table_data(output_results, output_tsv)

if __name__ == "__main__":
    main()

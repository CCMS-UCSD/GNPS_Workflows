#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import ming_proteosafe_library
import ming_fileio_library

def main():
    parser = argparse.ArgumentParser(description='Create parallel parameters')
    parser.add_argument('library_folder', help='Input mgf file to network')
    parser.add_argument('workflow_parameters', help='proteosafe xml parameters')
    parser.add_argument('parameters_output_folder', help='output folder for parameters')
    parser.add_argument('--parallelism', default=1, type=int, help='Parallelism')
    args = parser.parse_args()

    params_object = ming_proteosafe_library.parse_xml_file(open(args.workflow_parameters))

    library_files = ming_fileio_library.list_files_in_dir(args.library_folder)

    for i in range(args.parallelism):
        output_parameter_file = open(os.path.join(args.parameters_output_folder, str(i) + ".params"), "w")
        #Search Criteria
        output_parameter_file.write("MIN_MATCHED_PEAKS=%s\n" % (params_object["MIN_MATCHED_PEAKS"][0]))
        output_parameter_file.write("TOP_K_RESULTS=%s\n" % (params_object["TOP_K_RESULTS"][0]))
        output_parameter_file.write("search_peak_tolerance=%s\n" % (params_object["tolerance.Ion_tolerance"][0]))
        output_parameter_file.write("search_parentmass_tolerance=%s\n" % (params_object["tolerance.PM_tolerance"][0]))
        output_parameter_file.write("ANALOG_SEARCH=%s\n" % (params_object["ANALOG_SEARCH"][0]))
        output_parameter_file.write("MAX_SHIFT_MASS=%s\n" % (params_object["MAX_SHIFT_MASS"][0]))
        output_parameter_file.write("SEARCH_LIBQUALITY=%s\n" % (params_object["SEARCH_LIBQUALITY"][0]))

        #Filtering Criteria
        output_parameter_file.write("FILTER_PRECURSOR_WINDOW=%s\n" % (params_object["FILTER_PRECURSOR_WINDOW"][0]))
        output_parameter_file.write("MIN_PEAK_INT=%s\n" % (params_object["MIN_PEAK_INT"][0]))
        output_parameter_file.write("WINDOW_FILTER=%s\n" % (params_object["WINDOW_FILTER"][0]))
        output_parameter_file.write("FILTER_LIBRARY=%s\n" % (params_object["FILTER_LIBRARY"][0]))

        output_parameter_file.write("NODEIDX=%d\n" % (i))
        output_parameter_file.write("NODECOUNT=%d\n" % (args.parallelism))


        #For GC
        output_parameter_file.write("FORCE_EXACT_MATCH=%s\n" % (params_object["FORCE_EXACT_MATCH"][0]))

        #Libraries
        output_parameter_file.write("EXISTING_LIBRARY_MGF=%s\n" % (" ".join(library_files)))

        output_parameter_file.close()





if __name__ == "__main__":
    main()

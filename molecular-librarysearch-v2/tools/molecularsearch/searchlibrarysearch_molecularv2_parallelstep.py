#!/usr/bin/python


import sys
import getopt
import os
import json
import argparse
import uuid
from collections import defaultdict
import ming_proteosafe_library
import ming_fileio_library
import ming_parallel_library

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def search_wrapper(search_param_dict):
    search_files(search_param_dict["spectra_files"], search_param_dict["temp_folder"], search_param_dict["tempresults_folder"], search_param_dict["args"], search_param_dict["params_object"], search_param_dict["library_files"])

def search_files(spectra_files, temp_folder, tempresults_folder, args, params_object, library_files):
    parameter_filename = os.path.join(temp_folder, str(uuid.uuid4()) + ".params")
    output_parameter_file = open(parameter_filename, "w")

    #Search Criteria
    output_parameter_file.write("MIN_MATCHED_PEAKS_SEARCH=%s\n" % (params_object["MIN_MATCHED_PEAKS"][0]))
    output_parameter_file.write("TOP_K_RESULTS=%s\n" % (params_object["TOP_K_RESULTS"][0]))
    output_parameter_file.write("search_peak_tolerance=%s\n" % (params_object["tolerance.Ion_tolerance"][0]))
    output_parameter_file.write("search_parentmass_tolerance=%s\n" % (params_object["tolerance.PM_tolerance"][0]))
    output_parameter_file.write("ANALOG_SEARCH=%s\n" % (params_object["ANALOG_SEARCH"][0]))
    output_parameter_file.write("MAX_SHIFT_MASS=%s\n" % (params_object["MAX_SHIFT_MASS"][0]))

    #Filtering Criteria
    output_parameter_file.write("FILTER_PRECURSOR_WINDOW=%s\n" % (params_object["FILTER_PRECURSOR_WINDOW"][0]))
    output_parameter_file.write("MIN_PEAK_INT=%s\n" % (params_object["MIN_PEAK_INT"][0]))
    output_parameter_file.write("WINDOW_FILTER=%s\n" % (params_object["WINDOW_FILTER"][0]))
    output_parameter_file.write("FILTER_LIBRARY=%s\n" % (params_object["FILTER_LIBRARY"][0]))

    #Scoring Criteria
    output_parameter_file.write("SCORE_THRESHOLD=%s\n" % (params_object["SCORE_THRESHOLD"][0]))

    #Output
    output_parameter_file.write("RESULTS_DIR=%s\n" % (os.path.join(tempresults_folder, str(uuid.uuid4()) + ".tsv")))

    output_parameter_file.write("NODEIDX=%d\n" % (0))
    output_parameter_file.write("NODECOUNT=%d\n" % (1))

    output_parameter_file.write("EXISTING_LIBRARY_MGF=%s\n" % (" ".join(library_files)))

    all_query_spectra_list = []
    for spectrum_file in spectra_files:
        fileName, fileExtension = os.path.splitext(os.path.basename(spectrum_file))
        output_filename = ""

        if spectrum_file.find("mzXML") != -1 or spectrum_file.find("mzxml") != -1 or spectrum_file.find("mzML") != -1:
            output_filename = os.path.join(temp_folder, fileName + ".pklbin")
            cmd = "%s %s %s" % (args.convert_binary, spectrum_file, output_filename)
            print(cmd)
            os.system(cmd)
        else:
            output_filename = os.path.join(temp_folder, os.path.basename(spectrum_file))
            cmd = "cp %s %s" % (spectrum_file, output_filename)
            os.system(cmd)

        #Input
        faked_output_filename = os.path.join(temp_folder, os.path.basename(spectrum_file))
        all_query_spectra_list.append(faked_output_filename)


    output_parameter_file.write("searchspectra=%s\n" % (" ".join(all_query_spectra_list)))
    output_parameter_file.close()

    cmd = "%s ExecSpectralLibrarySearchMolecular %s -ccms_input_spectradir %s -ccms_results_prefix %s -ll 9" % (args.librarysearch_binary, parameter_filename, temp_folder, tempresults_folder)
    print(cmd)
    os.system(cmd)

        #Removing the spectrum
        # try:
        #     os.remove(output_filename)
        # except:
        #     print("Can't remove", output_filename)


def main():
    parser = argparse.ArgumentParser(description='Running library search parallel')
    parser.add_argument('spectra_folder', help='spectrafolder')
    parser.add_argument('json_parameters', help='proteosafe xml parameters')
    parser.add_argument('workflow_parameters', help='output folder for parameters')
    parser.add_argument('library_folder', help='output folder for parameters')
    parser.add_argument('result_folder', help='output folder for parameters')
    parser.add_argument('convert_binary', help='output folder for parameters')
    parser.add_argument('librarysearch_binary', help='output folder for parameters')
    parser.add_argument('--parallelism', default=1, type=int, help='Parallelism')
    args = parser.parse_args()

    parallel_json = json.loads(open(args.json_parameters).read())

    params_object = ming_proteosafe_library.parse_xml_file(open(args.workflow_parameters))
    mangled_mapping = ming_proteosafe_library.get_mangled_file_mapping(params_object)
    library_files = ming_fileio_library.list_files_in_dir(args.library_folder)
    spectra_files = ming_fileio_library.list_files_in_dir(args.spectra_folder)

    spectra_files.sort()

    print(spectra_files)
    spectra_files = spectra_files[parallel_json["node_partition"]::parallel_json["total_paritions"]]
    print(spectra_files)

    temp_folder = "temp"
    try:
        os.mkdir(temp_folder)
    except:
        print("folder error")

    tempresults_folder = "tempresults"
    try:
        os.mkdir(tempresults_folder)
    except:
        print("folder error")


    list_of_spectrumfiles = chunks(spectra_files, 5)
    parameter_list = []
    for spectrum_files_chunk in list_of_spectrumfiles:
        param_dict = {}
        param_dict["spectra_files"] = spectrum_files_chunk
        param_dict["temp_folder"] = temp_folder
        param_dict["tempresults_folder"] = tempresults_folder
        param_dict["args"] = args
        param_dict["params_object"] = params_object
        param_dict["library_files"] = library_files

        parameter_list.append(param_dict)

    #for param_dict in parameter_list:
    #    search_wrapper(param_dict)
    print("Parallel to execute", len(parameter_list))
    ming_parallel_library.run_parallel_job(search_wrapper, parameter_list, 5)


    """Merging Files and adding full path"""
    all_result_files = ming_fileio_library.list_files_in_dir(tempresults_folder)
    full_result_list = []
    for input_file in all_result_files:
        result_list = ming_fileio_library.parse_table_with_headers_object_list(input_file)
        full_result_list += result_list

    for result_object in full_result_list:
        mangled_name = os.path.basename(result_object["SpectrumFile"])
        full_path = mangled_mapping[mangled_name]
        result_object["full_CCMS_path"] = full_path

    ming_fileio_library.write_list_dict_table_data(full_result_list, os.path.join(args.result_folder, str(uuid.uuid4()) + ".tsv"))









if __name__ == "__main__":
    main()

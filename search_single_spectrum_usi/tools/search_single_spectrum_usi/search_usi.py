#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
import ming_proteosafe_library
import pandas as pd
import requests
import time

def _get_spectrum(usi):
    try:
        r = requests.get("https://metabolomics-usi.ucsd.edu/json/?usi={}".format(usi))
        return r.json()["precursor_mz"], r.json()["peaks"]
    except:
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Invoking new workflow with parameters of given workflow')
    parser.add_argument('workflowparamters', help='workflowparamters')
    parser.add_argument('credentials', help='credentials.json')
    parser.add_argument('outputresults', help='output params')
    args = parser.parse_args()

    workflow_parameters_map = ming_proteosafe_library.parse_xml_file(open(args.workflowparamters))

    usi_list = workflow_parameters_map["usi_string"][0].split("\n")
    usi_list = [usi for usi in usi_list if len(usi) > 5]

    all_tasks = []

    for usi in usi_list:
        invokeParameters = {}

        invokeParameters["desc"] = "Analysis subroutine from ProteoSAFe job %s" % (workflow_parameters_map["task"][0])
        invokeParameters["workflow"] = "SEARCH_SINGLE_SPECTRUM"
        invokeParameters["workflow_version"] = "release_28"
        invokeParameters["protocol"] = "None"
        invokeParameters["library_on_server"] = workflow_parameters_map["library_on_server"][0]

        #Search Parameters
        invokeParameters["tolerance.PM_tolerance"] = workflow_parameters_map["tolerance.PM_tolerance"][0]
        invokeParameters["tolerance.Ion_tolerance"] = workflow_parameters_map["tolerance.Ion_tolerance"][0]

        invokeParameters["ANALOG_SEARCH"] = workflow_parameters_map["ANALOG_SEARCH"][0]
        invokeParameters["FIND_MATCHES_IN_PUBLIC_DATA"] = "1"
        invokeParameters["MAX_SHIFT_MASS"] = "100"
        invokeParameters["MIN_MATCHED_PEAKS"] = workflow_parameters_map["MIN_MATCHED_PEAKS"][0]
        invokeParameters["SCORE_THRESHOLD"] = workflow_parameters_map["SCORE_THRESHOLD"][0]
        invokeParameters["SEARCH_LIBQUALITY"] = "3"
        invokeParameters["SEARCH_RAW"] = "0"
        invokeParameters["TOP_K_RESULTS"] = "1"
        invokeParameters["DATABASES"] = workflow_parameters_map["DATABASES"][0]

        #Filter Parameters
        invokeParameters["FILTER_LIBRARY"] = workflow_parameters_map["FILTER_LIBRARY"][0]
        invokeParameters["FILTER_PRECURSOR_WINDOW"] = workflow_parameters_map["FILTER_PRECURSOR_WINDOW"][0]
        invokeParameters["FILTER_SNR_PEAK_INT"] = workflow_parameters_map["FILTER_SNR_PEAK_INT"][0]
        invokeParameters["FILTER_STDDEV_PEAK_INT"] = workflow_parameters_map["FILTER_STDDEV_PEAK_INT"][0]
        invokeParameters["MIN_PEAK_INT"] = workflow_parameters_map["MIN_PEAK_INT"][0]
        invokeParameters["WINDOW_FILTER"] = workflow_parameters_map["WINDOW_FILTER"][0]

        # Post Parameters
        invokeParameters["CREATE_NETWORK"] = "No"

        #Spectrum
        precursor_mz, peaks = _get_spectrum(usi)
        if precursor_mz == None:
            continue

        invokeParameters["precursor_mz"] = precursor_mz
        invokeParameters["spectrum_string"] = "\n".join(["{}\t{}".format(peak[0], peak[1]) for peak in peaks])

        invokeParameters["email"] = "nobody@ucsd.edu"
        invokeParameters["uuid"] = "1DCE40F7-1211-0001-979D-15DAB2D0B500"

        credentials = json.loads(open(args.credentials).read())
        task_id = ming_proteosafe_library.invoke_workflow("gnps.ucsd.edu", invokeParameters, credentials["username"], credentials["password"])
        if task_id == None:
            continue
        all_tasks.append({"usi" : usi, "task_id" : task_id})

        time.sleep(120)
    
    for task in all_tasks:
        ming_proteosafe_library.wait_for_workflow_finish("gnps.ucsd.edu", task["task_id"])

    tasks_df = pd.DataFrame(all_tasks)
    tasks_df.to_csv(args.outputresults, sep="\t", index=False)

if __name__ == "__main__":
    main()

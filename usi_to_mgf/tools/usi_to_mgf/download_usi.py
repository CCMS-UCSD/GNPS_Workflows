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
    parser.add_argument('outputresults', help='output folder')
    args = parser.parse_args()

    workflow_parameters_map = ming_proteosafe_library.parse_xml_file(open(args.workflowparamters))

    usi_list = workflow_parameters_map["usi_string"][0].split("\n")
    usi_list = [usi for usi in usi_list if len(usi) > 5]

    all_tasks = []

    output_mgf = open(os.path.join(args.outputresults, "specs_ms.mgf"), "w")


    for i, usi in enumerate(usi_list):
        #Spectrum
        precursor_mz, peaks = _get_spectrum(usi)
        if precursor_mz == None:
            continue

        output_mgf.write("BEGIN IONS\n")
        output_mgf.write("TITLE=USI:{}\n".format(usi))
        output_mgf.write("PEPMASS={}\n".format(precursor_mz))
        output_mgf.write("CHARGE=0\n")
        output_mgf.write("SCANS={}\n".format(i + 1))
        for peak in peaks:
            output_mgf.write("{} {}\n".format(peak[0], peak[1]))
            output_mgf.write("\n")
        output_mgf.write("END IONS\n")

    tasks_df = pd.DataFrame(all_tasks)
    tasks_df.to_csv(args.outputresults, sep="\t", index=False)

if __name__ == "__main__":
    main()

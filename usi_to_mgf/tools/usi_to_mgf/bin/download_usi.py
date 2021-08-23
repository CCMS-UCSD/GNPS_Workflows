#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse
import pandas as pd
import requests
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "shared_code"))
import ming_proteosafe_library

def _get_spectrum(usi):
    try:
        print(usi)
        r = requests.get("https://metabolomics-usi.ucsd.edu/json/", params={"usi1": usi})
        return r.json()["precursor_mz"], r.json()["peaks"]
    except:
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Invoking new workflow with parameters of given workflow')
    parser.add_argument('workflowparamters', help='workflowparamters')
    parser.add_argument('output_mgf', help='output_mgf')
    parser.add_argument('output_tsv', help='output_tsv')
    args = parser.parse_args()

    workflow_parameters_map = ming_proteosafe_library.parse_xml_file(open(args.workflowparamters))

    usi_list = workflow_parameters_map["usi_string"][0].split("\n")
    usi_list = [usi for usi in usi_list if len(usi) > 5]

    output_mgf = open(args.output_mgf, "w")

    output_results_list = []

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
        output_mgf.write("END IONS\n")

        output_dict = {}
        output_dict["usi"] = usi
        output_dict["filename"] = args.output_mgf
        output_dict["scan"] = i + 1

        output_results_list.append(output_dict)

    df = pd.DataFrame(output_results_list)
    df.to_csv(args.output_tsv, sep="\t", index=False)


if __name__ == "__main__":
    main()

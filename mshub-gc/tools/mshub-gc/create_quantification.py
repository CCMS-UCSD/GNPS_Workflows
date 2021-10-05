#!/usr/bin/python

import pandas as pd
import sys
import getopt
import os
import argparse
import subprocess
import proteosafe
from collections import defaultdict

def load_feature_to_rt_mapping(integrals_filename):
    mapping = {}

    df = pd.read_csv(integrals_filename)

    mapping_record = df.to_dict(orient="records")[0]

    for key in mapping_record:
        if key == "No:":
            continue
        mapping[key] = mapping_record[key].split(" ")[0]

    return mapping

def convert_quantification(input_integrals_filename, workflow_parameters, output_filename):
    params_obj = proteosafe.parse_xml_file(workflow_parameters)
    mangled_mapping = proteosafe.get_mangled_file_mapping(params_obj)
    all_input_filename = [os.path.basename(mangled_mapping[key]) for key in mangled_mapping]

    filename_mapping = {}
    for filename in all_input_filename:
        removed_extension = os.path.splitext(filename)[0]
        filename_mapping[removed_extension] = filename

    integrals_df = pd.read_csv(input_integrals_filename, skiprows=[1,2,3])

    feature_to_rt_mapping = load_feature_to_rt_mapping(input_integrals_filename)

    all_molecules = list(integrals_df.keys())
    all_molecules.remove("No:")

    output_list = []
    for molecule in all_molecules:
        output_dict = {}
        output_dict["row ID"] = molecule
        output_dict["row m/z"] = "0"
        output_dict["row retention time"] = feature_to_rt_mapping[molecule]
        for record in integrals_df.to_dict(orient="records"):
            sample_name = record["No:"]
            abundance = record[molecule]

            if sample_name in filename_mapping:
                sample_name = filename_mapping[sample_name]
            output_dict[str(sample_name) + " Peak area"] = abundance

        output_list.append(output_dict)

    pd.DataFrame(output_list).to_csv(output_filename, sep=",", index=False)

def main():
    parser = argparse.ArgumentParser(description='Processing and feature detecting all gc files')
    parser.add_argument('preprocessing_scratch', help='preprocessing_scratch')
    parser.add_argument('workflow_parameters', help='workflow_parameters')
    parser.add_argument('quantification_output', help='quantification_output')
    args = parser.parse_args()

    input_integrals_filename = os.path.join(args.preprocessing_scratch, "data_integrals.csv")

    convert_quantification(input_integrals_filename, args.workflow_parameters, args.quantification_output)




if __name__ == "__main__":
    main()

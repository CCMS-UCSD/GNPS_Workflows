#!/usr/bin/python

import pandas as pd
import sys
import getopt
import os
import argparse
import subprocess
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description='Processing and feature detecting all gc files')
    parser.add_argument('preprocessing_scratch', help='preprocessing_scratch')
    parser.add_argument('quantification_output', help='quantification_output')
    args = parser.parse_args()

    input_integrals_filename = os.path.join(args.preprocessing_scratch, "data_integrals.csv")

    integrals_df = pd.read_csv(input_integrals_filename, skiprows=[1,2,3])

    all_molecules = list(integrals_df.keys())
    all_molecules.pop("No:")

    output_list = []
    for molecule in all_molecules:
        output_dict = {}
        output_dict["row ID"] = molecule
        output_dict["row m/z"] = "0"
        output_dict["row RT"] = "0"
        for record in integrals_df.to_dict(orient="records"):
            sample_name = record["No:"]
            abundance = record[molecule]
            output_dict[sample_name + " Peak area"] = abundance

        output_list.append(output_dict)

    pd.DataFrame(output_list).to_csv(args.quantification_output, sep=",", index=False)




if __name__ == "__main__":
    main()

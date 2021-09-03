#!/usr/bin/python

import sys
import getopt
import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run networking')
    parser.add_argument('networking_parameters', help='networking_parameters')
    parser.add_argument('ccms_output_aligns', help='ccms_output_aligns')
    parser.add_argument('input_spectra', help='input_spectra')
    parser.add_argument('main_execmodule', help='path to main_execmodule')
    args = parser.parse_args()

    cmd = "{} ExecMolecularParallelPairs {} -ccms_output_aligns {} -ccms_INPUT_SPECTRA_MS2 {}".format(args.main_execmodule, 
        args.networking_parameters, 
        args.ccms_output_aligns,
        args.input_spectra)

    print(cmd)
    status_code = os.system(cmd)

    if not os.path.exists(args.ccms_output_aligns):
        open(args.ccms_output_aligns, "w").write("CLUSTERID1\tCLUSTERID2\tDeltaMZ\tMinRatio\tCosine\tAlignScore2\tAlignScore3\n")

    # if status_code != 0:
    #     exit(status_code)

    


if __name__ == "__main__":
    main()

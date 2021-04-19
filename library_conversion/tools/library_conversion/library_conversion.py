#!/usr/bin/python

import os
import sys
import argparse
import nist_msp_conversion as msp_convert
import mzvault_conversion as mzvault_convert

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-input-library", dest="input_filename")
    parser.add_argument("--output-folder", dest="outfolder", default=None)
    parser.add_argument("--mgf-file", dest="mgf_filename", default=None)
    parser.add_argument("--csv-file", dest="csv_filename", default=None)

    args = parser.parse_args()

    if args.input_filename is None:
        print("Error: Either provide 2 arguments (input file, output folder) or three arguments (input file, "
              "mgf output file, csv table output file)")
        parser.print_help(sys.stderr)
        sys.exit(1)


    input_filename = args.input_filename

    has_outfile_args = args.mgf_filename is not None and args.csv_filename is not None

    if args.outfolder is not None and has_outfile_args == False:
        # only 2 args: input_file, output_folder
        # strip extension and path to get filename
        base_filename = os.path.splitext(os.path.basename(input_filename))[0]
        mgf_filename = os.path.join(args.outfolder, "{}.mgf".format(base_filename))
        batch_filename = os.path.join(args.outfolder, "{}.csv".format(base_filename))

    elif has_outfile_args:
        mgf_filename = args.mgf_filename
        batch_filename = args.csv_filename
    else:
        print("Error: Either provide 2 arguments (input file, output folder) or three arguments (input file, "
              "mgf output file, csv table output file)")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # convert nist msp or MZVault file
    if input_filename.lower().endswith(".msp"):
        msp_convert.convert(input_filename, mgf_filename, batch_filename)
    else :
        mzvault_convert.convert(input_filename, mgf_filename, batch_filename)

    # success
    sys.exit(0)

if __name__ == "__main__":
    main()
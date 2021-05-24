#!/usr/bin/python

import os
import sys
import argparse
from enum import Enum


# Specifies the input formats
class InputFormat(Enum):
    mzvault, nist_msp, mzmine_json, bmdms = range(4)


# handle formats and convert
def convert(libformat, input_filename, mgf_filename, batch_filename, pi_name, collector_name):
    num_library_entries = 0
    if libformat == InputFormat.mzvault.name:
        import mzvault_conversion
        num_library_entries = mzvault_conversion.convert(input_filename, mgf_filename, batch_filename, pi_name,
                                                         collector_name)
    elif libformat == InputFormat.nist_msp.name:
        import nist_msp_conversion
        num_library_entries = nist_msp_conversion.convert(input_filename, mgf_filename, batch_filename, pi_name,
                                                          collector_name)
    elif libformat == InputFormat.bmdms.name:
        import bmdms_conversion
        num_library_entries = bmdms_conversion.convert(input_filename, mgf_filename, batch_filename, pi_name,
                                                       collector_name)
    elif libformat == InputFormat.mzmine_json.name:
        import mzmine_json_conversion
        num_library_entries = mzmine_json_conversion.convert(input_filename, mgf_filename, batch_filename, pi_name,
                                                             collector_name)
    return num_library_entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-input-library", dest="input_filename")
    parser.add_argument("--output-folder", dest="outfolder", default=None,
                        help="Define the output folder to create files with the input file name. Do not combine with "
                             "mgf-file and csv-file arguments.")
    parser.add_argument("--mgf-file", dest="mgf_filename", default=None,
                        help="Combine mgf-file with csv-file to define the output. Do not combine with output-folder")
    parser.add_argument("--csv-file", dest="csv_filename", default=None)
    parser.add_argument('--pi', dest="pi_name", default=None)
    parser.add_argument('--collector', dest="collector_name", default=None)
    parser.add_argument("--libformat", dest="libformat",
                        default=InputFormat.mzvault,
                        help="Specify input format as one of: {}".format(
                            ", ".join(str(e.name) for e in list(InputFormat))))

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
        batch_filename = os.path.join(args.outfolder, "{}.tsv".format(base_filename))

    elif has_outfile_args:
        mgf_filename = args.mgf_filename
        batch_filename = args.csv_filename
    else:
        print("Error: Either provide 2 arguments (input file, output folder) or three arguments (input file, "
              "mgf output file, csv table output file)")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # convert based on input format
    libformat = str(args.libformat).lower()
    try:
        num_library_entries = convert(libformat, input_filename, mgf_filename, batch_filename, args.pi_name,
                                      args.collector_name)

        if num_library_entries == 0:
            sys.exit(1)  # exit with error
    except:
        sys.exit(1)  # exit with error
    # success
    sys.exit(0)


if __name__ == "__main__":
    main()

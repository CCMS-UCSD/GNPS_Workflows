#!/usr/bin/python

import os
import sys
import nist_msp_conversion as msp_convert
import mzvault_conversion as mzvault_convert


input_filename = sys.argv[1]
mgf_filename = ""
batch_filename = ""

if len(sys.argv) > 2:
    mgf_filename = sys.argv[2]
    batch_filename = sys.argv[3]
else:
    # only 2 args: input_file, output_folder
    # strip extension and path to get filename
    base_filename = os.path.splitext(os.path.basename(input_filename))[0]
    out_folder = sys.argv[2]
    mgf_filename = os.path.join(out_folder, "{}.mgf".format(base_filename))
    batch_filename = os.path.join(out_folder, "{}.csv".format(base_filename))

if input_filename.lower().endswith(".msp"):
    msp_convert.convert(input_filename, mgf_filename, batch_filename)
else :
    mzvault_convert.convert(input_filename, mgf_filename, batch_filename)
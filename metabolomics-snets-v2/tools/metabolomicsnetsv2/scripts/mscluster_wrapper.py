#!/usr/bin/python

import sys
import os
import glob

def usage():
    print("<input spectra> <parameters filename> <output spectra> <output aligns> <main specnets filepath>")

def main():
    usage()

    input_spectra_folder = sys.argv[1]
    parameters_filename = sys.argv[2]
    output_spectra_folder = sys.argv[3]
    output_alignments_folder = sys.argv[4]
    mainspecnets_binary = sys.argv[5]

    cmd = "%s %s -ll 9 -f mscluster" % (mainspecnets_binary, parameters_filename)
    ret_code = os.system(cmd)

    if ret_code != 0:
        exit(1)

    #Do clean up out output spectra folder
    all_pklbin_files = glob.glob(os.path.join(output_spectra_folder, "*.pklbin")
    print(all_pklbin_files)


if __name__ == "__main__":
    main()

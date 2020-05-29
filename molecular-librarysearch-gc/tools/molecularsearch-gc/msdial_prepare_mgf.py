#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 2020 by Louis Felix

@author: Louis Felix Nothias
@purpose: prepare the MS-DIAL MGF file into a diserable format for GC-MS analysis on GNPS
"""
import sys

def prepare_mgf(input_filename,output_filename):
    with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
        # Here we look for a line with SCANS and we replace the value
        i = 0
        for line in input_file:
            if 'SCANS' in line:
                i += 1
                line = 'SCANS='+str(i)+"\n"
                output_file.write(line)
            else:
                output_file.write(line)

        return

if __name__=="__main__":
    # Provide the input filename and output filename as arguments
    prepare_mgf(sys.argv[1], sys.argv[2])

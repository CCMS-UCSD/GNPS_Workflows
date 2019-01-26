#!/usr/bin/python

import sys
import getopt
import os
import ming_fileio_library
from collections import defaultdict

def main():
    input_library_identifications = sys.argv[1]
    output_library_identifications = sys.argv[2]

    annotations_list = ming_fileio_library.parse_table_with_headers_object_list(input_library_identifications)

    already_identified_compounds = set()
    already_identified_spectra = set()

    annotations_list = sorted(annotations_list, key=lambda identification: float(identification["MQScore"]), reverse=True)

    output_annotation_list = []
    for annotation in annotations_list:
        compound_name = annotation["Compound_Name"]
        spectrum_identifier = annotation["#Scan#"] + ":" + annotation["SpectrumFile"]

        if compound_name in already_identified_compounds:
            continue
        if spectrum_identifier in already_identified_spectra:
            continue

        print(compound_name, spectrum_identifier)

        output_annotation_list.append(annotation)
        already_identified_compounds.add(compound_name)
        already_identified_spectra.add(spectrum_identifier)

    ming_fileio_library.write_list_dict_table_data(output_annotation_list, output_library_identifications)



if __name__ == "__main__":
    main()

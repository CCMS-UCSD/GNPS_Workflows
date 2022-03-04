#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # Transform the header to be final result format
    input_quantification = pd.read_csv(input_filename,sep=',')

    if "row retention time" in input_quantification.keys():
        # check if MZmine 2
        convert_mzmine2_to_feature_csv(input_quantification, output_filename)
    else:
        # or MZmine 3
        convert_mzmine3_to_feature_csv(input_quantification, output_filename)

# Uses the MZmine 2 legacy csv export
def convert_mzmine2_to_feature_csv(input_quantification, output_filename):
    valid_extensions = [
        ".raw ",
        ".RAW ",
        ".mzML ",
        ".mzXML ",
        ".CDF ",
        ".d ",
        ".mgf ",
        ".MGF ",
        ".mzData ",
        ".lcd ",
        ".wiff ",
        ".scan ",
        ".tdf ",
        ".tsf "
    ]

    # intensity might be height or area but we keep "area" in the header for both to not break other tools
    intensity_type = "area"
    
    rename_mapping = {}
    for key in input_quantification.keys():
        # intensity might start with Peak area or height
        # resulting column will be renamed to Peak area even for height - to conserve the functionality of dependent
        # tools.
        if "Peak area" in key or "Peak height" in key:
            if "Peak height" in key:
                intensity_type = "height"

            # Removing everything after an expected extension
            for valid_extension in valid_extensions:
                if valid_extension in key:
                    end_index = key.rfind(valid_extension) + len(valid_extension) - 1
                    filename = key[:end_index]
                    print("Renaming", key, "to", filename + " Peak area")
                    rename_mapping[key] = filename + " Peak area"
                    continue

    input_quantification.rename(columns=rename_mapping, inplace=True)
    # add column for intensity measure
    input_quantification["intensity_measure"] = intensity_type
    # write to output
    input_quantification.to_csv(output_filename,index = False)

# takes the MZmine 3 full feature list to csv export
# renames to columns used by GNPS tools
def convert_mzmine3_to_feature_csv(input_quantification, output_filename):
    # rename columns
    rename_mapping = {}
    rename_mapping["id"] = "row ID"
    rename_mapping["mz"] = "row m/z"
    rename_mapping["rt"] = "row retention time"

    # IIMN
    if "feature_group" in input_quantification.keys():
        rename_mapping["feature_group"] = "correlation group ID"
    if "ion_identities:iin_id" in input_quantification.keys():
        rename_mapping["ion_identities:iin_id"] = "annotation network number"
        rename_mapping["ion_identities:ion_identities"] = "best ion"
        rename_mapping["ion_identities:partner_row_ids"] = "partners"
        rename_mapping["ion_identities:neutral_mass"] = "neutral M mass"
        rename_mapping["ion_identities:list_size"] = "identified by n="
        # rename_mapping["rt"] = "auto MS2 verify"

    # currently no option to set this in GNPS
    intensity_type = "area"

    for key in input_quantification.keys():
        # datafile:SAMPLE_NAME.mzML:area --> SAMPLE_NAME.mzML Peak area
        if "datafile" in key and "area" in key:
            filename = key.split(":")[1]
            print("Renaming", key, "to", filename + " Peak area")
            rename_mapping[key] = filename + " Peak area"
            continue

    input_quantification.rename(columns=rename_mapping, inplace=True)
    # add column for intensity measure
    input_quantification["intensity_measure"] = intensity_type
    # write to output
    input_quantification.to_csv(output_filename,index = False)

###function verifies that the quant table follows proper mzmine format
def validate_mzmine_output_file(quant_table_filename):
    required_columns = ["row ID", "row retention time", "row m/z"]
    file_open = open(quant_table_filename, 'r')
    first_line = next(file_open)

    #try splitting it by comma
    all_columns_list = first_line.split(",")
    
    #make sure the mandatory headings are in the file
    assert(set(required_columns).issubset(set(all_columns_list)))

if __name__=="__main__":
    # there should be only one input file
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

    try:
        validate_mzmine_output_file(sys.argv[2])
        exit(0)
    except:
        exit(1)

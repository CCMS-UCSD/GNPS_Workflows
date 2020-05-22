#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the Progensis output into a diserable format
"""
import pandas as pd
import sys

def convert_to_feature_csv(input_filename, output_filename):
    # First read the table and deduce the number of samples from the difference between Norm abundance and RAW abundance (skiprows=0)
    input_format_for_raw_position = pd.read_csv(input_filename, sep=",", skiprows=0)
    index_RAW = input_format_for_raw_position.columns.get_loc('Raw abundance')
    index_Norm = input_format_for_raw_position.columns.get_loc('Normalised abundance')
    assumed_number_of_samples = len(input_format_for_raw_position.iloc[:,index_Norm:index_RAW].columns)

    #Check requirements for the table
    required_names = ["Raw abundance", "Normalised abundance"]
    for require_name in required_names:
        if not require_name in input_format_for_raw_position:
            raise Exception("Missing Column, please verify the format on the Progenesis QI {}".format(require_name))

    # Now read again the table for the samples and metadata column name (skiprows=2)
    input_format = pd.read_csv(input_filename, sep=",", skiprows=2, encoding ='utf-8')

    #Check requirements for the table
    required_names = ["Compound", "Retention time (min)", "m/z"]
    for require_name in required_names:
        if not require_name in input_format:
            raise Exception("Missing Column, please verify the format on the Progenesis QI {}".format(require_name))

    #Get the metadata columns before samples
    columns_left = input_format.iloc[:,:index_Norm].columns.to_list()
    #Get the metadata columns after the samples
    columns_right_index = index_Norm+assumed_number_of_samples
    columns_right = input_format.iloc[:,columns_right_index:].columns.to_list()
    non_sample_names = columns_left + columns_right

    #delimiting the samples
    sample_names = [header for header in input_format.keys() if not header in non_sample_names and not header[-2:] == ".1"]

    #Making a dictionary
    input_records = input_format.to_dict(orient="records")

    output_records = []
    output_records2 = []
    compound_to_scan_mapping = {}
    running_scan = 0
    for record in input_records:
        running_scan += 1

        compound_name = record["Compound"]
        mz = record["m/z"]
        rt = record["Retention time (min)"]

        output_record = {}

        output_record["row ID"] = str(running_scan)
        output_record["row m/z"] = float(mz)
        output_record["row retention time"] = float(rt)

        output_record2 = {}
        for sample_name in sample_names:
            output_record2[sample_name + " Peak area"] = record[sample_name]

        #Adding extra columns that are not sample_names
        for key in record:
            if key in sample_names:   ###
                continue
            try:
                output_record[key] = record[key]
            except:
                continue

        output_records.append(output_record)
        output_records2.append(output_record2)

        compound_to_scan_mapping[compound_name] = running_scan

        # Prepared the processed tables

    output_df = pd.DataFrame(output_records)
    output_df = output_df.drop([x for x in output_df if x.endswith('.1')], 1)

    output_df2 = pd.DataFrame(output_records2)
    output_df_prepared = pd.concat([output_df, output_df2], axis=1)

        # Round value for retention time column
    output_df_prepared['row retention time'] =  output_df_prepared['row retention time'].astype(float)
    output_df_prepared['row retention time'] =  output_df_prepared['row retention time'].apply(lambda x: round(x, 3))

    newdf = output_df_prepared

    # Drop the column with weird characters and mess with the CSV format
    if 'Accepted Description' in newdf.columns:
        newdf = newdf.drop(['Accepted Description'], axis=1)

    # Rename column name for consistency with other tools supported by FBMN
    if 'Formula' in newdf.columns:
        newdf.rename(columns={'Formula':'Molecular Formula'}, inplace=True)
    if 'Neutral mass (Da)' in newdf.columns:
        newdf.rename(columns={'Neutral mass (Da)':'Neutral mass'}, inplace=True)
    if 'CCS (angstrom^2)' in newdf.columns:
        newdf.rename(columns={'CCS (angstrom^2)':'CCS'}, inplace=True)
    if 'dCCS (angstrom^2)' in newdf.columns:
        newdf.rename(columns={'dCCS (angstrom^2)':'dCCS'}, inplace=True)

    ## Drop useless duplicated columns
    if 'm/z' in newdf.columns:
        newdf = newdf.drop(['m/z'], axis=1)
    if 'Retention time (min)' in newdf.columns:
        newdf = newdf.drop(['Retention time (min)'], axis=1)

    #Round values for columns
    newdf['Neutral mass'] = newdf['Neutral mass'].apply(lambda x: round(x, 4))
    newdf['Chromatographic peak width (min)'] = newdf['Chromatographic peak width (min)'].apply(lambda x: round(x, 3))

    #Write out the table
    newdf.to_csv(str(output_filename), sep=",", index=False)

    return compound_to_scan_mapping

#Converts MSP to MGF
def convert_mgf(input_msp, output_mgf, compound_to_scan_mapping):
    output_filename = open(output_mgf, "w")
    read_name = False

    scan = -1
    precursor_mz = -1
    charge = -1
    peaks = []

    # This is a stop gap solution to make sure we don't have repetitions in the MGF file.
    # We only take one MS2 arbitrarily selected and output into the MGF file
    observed_compound_names = set()

    for line in open(input_msp):
        if line.startswith("Comment:"):
            compound_name = line.rstrip().replace("Comment: ", "")
            comment = line.rstrip().replace("Comment: ", "FILENAME=")
            ret_time = line.rstrip().replace("Comment: ", "").replace("_", "__")
            sep = '__'
            ret_time = ret_time.split(sep, 1)[0]

            if compound_name in observed_compound_names:
                print("skipping repeated feature")
                continue

            observed_compound_names.add(compound_name)

            read_name = True
            scan = (compound_to_scan_mapping[compound_name])

        if line.startswith("PrecursorMZ:"):
            precursor_mz = (line.rstrip().replace("PrecursorMZ: ", "PEPMASS="))
        if line.startswith("Charge:"):
            charge = []
            charge = (line.rstrip().replace("Charge: ", "CHARGE="))
            precursor_type = []
        elif line.startswith("Precursor_type:"):
            precursor_type = []
            precursor_type = line.rstrip().replace("Precursor_type: ", "ION=")
            charge = []
        if len(line.rstrip()) == 0 and read_name == True:
            read_name = False

            output_filename.write("BEGIN IONS\n")
            output_filename.write("SCANS=%s\n" % (compound_to_scan_mapping[compound_name]))
            output_filename.write("FEATURE_ID=%s\n" % (compound_to_scan_mapping[compound_name]))
            output_filename.write("MSLEVEL=2\n")
            output_filename.write(str(precursor_mz)+"\n")
            if type(precursor_type) == str:
                output_filename.write(str(precursor_type)+"\n")
                if precursor_type[-2] == ']':
                    output_filename.write("CHARGE=1"+str(precursor_type[-1])+"\n")
                if precursor_type[-2] == '2':
                    output_filename.write("CHARGE=2"+str(precursor_type[-1])+"\n")
            elif type(charge) != '[]':
                    output_filename.write(str(charge)+"\n")

            output_filename.write(str(comment)+"\n")
            output_filename.write("RTINMINUTES="+str(ret_time)+"\n")
            for peak in peaks:
                output_filename.write("%f %f\n" % (peak[0], peak[1]))
            output_filename.write("END IONS\n\n")

            scan = -1
            precursor_mz = -1
            charge = -1
            peaks = []
        else:
            try:
                mass = float(line.split(" ")[0])
                intensity = float(line.split(" ")[1])
                peaks.append([mass, intensity])
            except:
                continue
    return

if __name__=="__main__":
    convert_to_feature_csv(sys.argv[1], sys.argv[2])

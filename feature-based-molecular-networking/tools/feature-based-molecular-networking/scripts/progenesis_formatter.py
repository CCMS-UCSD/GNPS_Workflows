#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the Progensis output into a diserable format
"""
import pandas as pd
import sys


#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_csv(input_filename, output_filename):
    input_format = pd.read_csv(input_filename, sep=",", skiprows=2)

    required_names = ["Compound", "Retention time (min)", "m/z"]
    for require_name in required_names:
        if not require_name in input_format:
            raise Exception("Missing Column {}".format(require_name))

    non_sample_names = ["Compound", "Neutral mass (Da)", "m/z", "Charge", "Retention time (min)", \
        "Chromatographic peak width (min)", "Identifications", "Isotope Distribution", "Maximum Abundance", \
        "Minimum CV%", "Accepted Compound ID", "Accepted Description", "Formula", \
        "Score", "Fragmentation Score", "Mass Error (ppm)", "Isotope Similarity", "Retention Time Error (mins)", "Compound Link", "Max Fold Change Peak area",
        "Highest Mean", "Lowest Mean","CCS (angstrom^2)","Anova (p)","q Value","Max Fold Change",
        "Max Ab > 100","High Samples","Anova p-value <= 0.05","Max fold change >= 1000","dCCS (angstrom^2)"]

    input_records = input_format.to_dict(orient="records")
    sample_names = [header for header in input_format.keys() if not header in non_sample_names and not header[-2:] == ".1"]

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
        output_record["row m/z"] = str(mz)
        output_record["row retention time"] = str(rt)

        output_record2 = {}
        for sample_name in sample_names:
            output_record2[sample_name + " Peak area"] = record[sample_name]

        #Adding in special columns for CCS
        if "CCS (angstrom^2)" in record:
            output_record["CCS"] = record["CCS (angstrom^2)"]
        if "dCCS (angstrom^2)" in record:
            output_record["dCCS"] = record["dCCS (angstrom^2)"]

        #Adding extra columns that are not sample_names
        for key in record:
            if key in sample_name:
                continue

            try:
                output_record[key] = record[key].encode("ascii", errors="replace")
            except:
                continue

        output_records.append(output_record)
        output_records2.append(output_record2)

        compound_to_scan_mapping[compound_name] = running_scan

    # Prepared the processed tables
    output_df = pd.DataFrame(output_records)
    output_df2 = pd.DataFrame(output_records2)
    output_df_prepared = pd.concat([output_df, output_df2], axis=1)
    
    # Round value for retention time column
    output_df_prepared['row retention time'] =  output_df_prepared['row retention time'].astype(float)
    output_df_prepared['row retention time'] =  output_df_prepared['row retention time'].apply(lambda x: round(x, 3))
    
    # Retrieved the metadata from the initial table
    newdf = input_format.loc[:, input_format.columns.isin(non_sample_names)]

    # Drop the column with weird characters and mess with the CSV format
    if 'Accepted Description' in newdf.columns:
        newdf = newdf.drop(['Accepted Description'], axis=1)

    # Rename column name for consistency
    if 'Formula' in newdf.columns:
        newdf.rename(columns={'Formula':'Molecular Formula'}, inplace=True)
    if 'Neutral mass (Da)' in newdf.columns:
        newdf.rename(columns={'Neutral mass (Da)':'Neutral mass'}, inplace=True)
    if 'CCS (angstrom^2)' in newdf.columns:
        newdf.rename(columns={'CCS (angstrom^2)':'CCS'}, inplace=True)
    if 'dCCS (angstrom^2)' in newdf.columns:
        newdf.rename(columns={'dCCS (angstrom^2)':'dCCS'}, inplace=True)
        
    # Drop useless duplicated columns
    if 'm/z' in newdf.columns:
        newdf = newdf.drop(['m/z'], axis=1)
    if 'Retention time (min)' in newdf.columns:
        newdf = newdf.drop(['Retention time (min)'], axis=1)
        
    #Round values for columns
    newdf['Neutral mass'] = newdf['Neutral mass'].apply(lambda x: round(x, 4))
    newdf['Chromatographic peak width (min)'] = newdf['Chromatographic peak width (min)'].apply(lambda x: round(x, 3))

    # Create the output table
    newdf_out = pd.concat([output_df_prepared,newdf],axis=1)

    # Remove duplicated columns
    if 'Compound' in newdf_out.columns: 
        newdf_out = newdf_out.drop(newdf_out.columns[0], axis=1)
    if 'Isotope Distribution' in newdf_out.columns: 
        newdf_out = newdf_out.drop(newdf_out.columns[0], axis=1)
     
    #Drop empty column   
    newdf_out = newdf_out.dropna(how='all', axis=1)
        
    newdf_out.to_csv(output_filename, sep=",", index=False)
    
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

            if compound_name in observed_compound_names:
                print("skipping repeated feature")
                continue

            observed_compound_names.add(compound_name)

            read_name = True
            scan = (compound_to_scan_mapping[compound_name])
        elif line.startswith("PrecursorMZ:"):
            precursor_mz = (line.rstrip().replace("PrecursorMZ: ", ""))
        elif line.startswith("Charge:"):
            charge = (line.rstrip().replace("Charge: ", ""))
        elif len(line.rstrip()) == 0 and read_name == True:
            read_name = False

            output_filename.write("BEGIN IONS\n")
            output_filename.write("SCANS=%s\n" % (compound_to_scan_mapping[compound_name]))
            output_filename.write("MSLEVEL=2\n")
            output_filename.write("CHARGE=%s\n" % (line.rstrip().replace("Charge: ", "")))
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

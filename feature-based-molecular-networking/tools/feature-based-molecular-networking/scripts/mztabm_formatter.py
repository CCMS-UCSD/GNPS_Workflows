#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mingxun Wang
@purpose: to convert the mztab output into a diserable format
"""
from io import StringIO
import pandas as pd
import sys
import os
import ming_spectrum_library

#TODO: Ask about why there are two column headers of the same name
def convert_to_feature_csv(input_filename, output_filename):
    MTD_lines = []
    SML_lines = []
    SMF_lines = []
    SME_lines = []

    for line in open(input_filename):
        if line.split("\t")[0] in ["SMH", "SML"]:
            SML_lines.append(line)
        if line.split("\t")[0] in ["SFH", "SMF"]:
            SMF_lines.append(line)
        if line.split("\t")[0] in ["SEH", "SME"]:
            SME_lines.append(line)
        if line.split("\t")[0] in ["MTD"]:
            MTD_lines.append(line)

    sml_data = pd.read_csv(StringIO("".join(SML_lines)), sep="\t")
    smf_data = pd.read_csv(StringIO("".join(SMF_lines)), sep="\t")
    sme_data = pd.read_csv(StringIO("".join(SME_lines)), sep="\t")

    #Parsing out metadata
    mtd_data = pd.read_csv(StringIO("".join(MTD_lines)), sep="\t", header=None)[[0, 1, 2]]
    mtd_data.columns = ['MTD', 'type', 'value']

    ms_run_to_filename = {}
    for record in mtd_data.to_dict(orient="records"):
        if "ms_run" in record["type"] and "location" in record["type"]:
            ms_run_to_filename[record["type"].split("-")[0]] = os.path.basename(record["value"])
    print(ms_run_to_filename)

    assay_to_msrun = {}
    for record in mtd_data.to_dict(orient="records"):
        if "assay" in record["type"] and "ms_run_ref" in record["type"]:
            assay_to_msrun[record["type"].split("-")[0]] = record["value"]
    print(assay_to_msrun)

    smf_to_scans = {}

    output_record_list = []
    for record in smf_data.to_dict(orient="records"):
        #Recording abundance
        output_dict = {}
        output_dict["row ID"] = record["SMF_ID"]
        output_dict["row m/z"] = record["exp_mass_to_charge"]
        output_dict["row retention time"] = record["retention_time_in_seconds"]

        for assay in assay_to_msrun:
            assay_abundance_key = "abundance_{}".format(assay)
            assay_abundance = record[assay_abundance_key]
            filename = ms_run_to_filename[assay_to_msrun[assay]]
            output_dict["{} Peak area".format(filename)] = assay_abundance

        output_record_list.append(output_dict)

        sme_id = str(record["SME_ID_REFS"])
        all_sme = [int(sme) for sme in sme_id.split("|")]

        #Looking up the filename
        sme_records = sme_data[sme_data["SME_ID"].isin(all_sme)]
        all_spectra_references = list(sme_records["spectra_ref"])
        all_spectra_references = [spectra_reference.split("|") for spectra_reference in all_spectra_references]
        all_spectra_references = [item for sublist in all_spectra_references for item in sublist]

        spectra_tuples = [(ms_run_to_filename[spectra_ref.split(":")[0].strip()], spectra_ref.split(":")[1]) for spectra_ref in all_spectra_references]

        smf_to_scans[record["SMF_ID"]] = spectra_tuples
    
    pd.DataFrame(output_record_list).to_csv(output_filename, sep=",", index=False)

    return smf_to_scans

#TODO: Finish this function to read the input files and find the MS2 and actually extract the peaks into an MGF
#TODO: Currently supports only mzML files
def create_mgf(input_filenames, output_mgf, compound_filename_mapping, name_mangle_mapping=None):
    spectrum_list = []
    
    print(name_mangle_mapping)

    for scan in compound_filename_mapping:
        #print(scan, compound_filename_mapping[scan])
        #Choosing one at random, the first, TODO: do a consensus or something like that
        target_ms2 = compound_filename_mapping[scan][0]

        filename_to_load = ""
        for input_filename in input_filenames:
            if target_ms2[0] in input_filename:
                filename_to_load = input_filename
            if name_mangle_mapping is not None:
                if target_ms2[0] in name_mangle_mapping:
                    filename_to_load = name_mangle_mapping[target_ms2[0]]

        if len(filename_to_load) == 0:
            continue

        #Find the right spectrum, should probably use proteowizard to do this
        spectrum_collection = ming_spectrum_library.SpectrumCollection(filename_to_load)
        spectrum_collection.load_from_file()

        query_identifier = target_ms2[1]
        query_scan = int(query_identifier.rstrip().split(" ")[-1].replace("scan=", ""))

        for spectrum in spectrum_collection.spectrum_list:
            if spectrum.scan == query_scan:
                spectrum.scan = scan
                spectrum_list.append(spectrum)
                print("Found Spectrum", query_scan, filename_to_load)
                break

    spectrum_collection = ming_spectrum_library.SpectrumCollection("")
    spectrum_collection.spectrum_list = spectrum_list
    spectrum_collection.save_to_mgf(open(output_mgf, "w"), renumber_scans=False)

    return None

if __name__=="__main__":
    # there should be obly one input file
   compound_filename_mapping = convert_to_feature_csv(sys.argv[1], sys.argv[2])

   import glob
   create_mgf(glob.glob(os.path.join(sys.argv[3], "*")), sys.argv[4], compound_filename_mapping)

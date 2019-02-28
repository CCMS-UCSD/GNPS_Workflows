#!/usr/bin/python


import sys
import os
import ming_fileio_library
import ming_gnps_library
from collections import defaultdict

def usage():
    print("<input clusterinfosummary file> <input edges file> <outptu file> ")


def main():
    input_result_filename = sys.argv[1]
    output_result_filename = sys.argv[2]

    spectrum_id_cache = {}


    input_rows, input_table = ming_fileio_library.parse_table_with_headers(input_result_filename)

    output_table = defaultdict(list)

    output_headers = ["SpectrumID", "Compound_Name", "Ion_Source", "Instrument", "Compound_Source", "PI", "Data_Collector", "Adduct"]
    output_headers += ["Precursor_MZ", "ExactMass", "Charge", "CAS_Number", "Pubmed_ID", "Smiles", "INCHI", "INCHI_AUX", "Library_Class"]
    output_headers += ["IonMode", "UpdateWorkflowName", "LibraryQualityString", "#Scan#", "SpectrumFile", "MQScore", "Organism"]
    output_headers += ["TIC_Query", "RT_Query", "MZErrorPPM", "SharedPeaks", "MassDiff", "LibMZ", "SpecMZ", "SpecCharge"]

    for header in output_headers:
        output_table[header] = []

    number_hits_per_query = defaultdict(lambda: 0)

    for i in range(input_rows):
        number_hits_per_query[input_table["FileScanUniqueID"][i]] += 1


    for i in range(input_rows):
        spectrum_id = input_table["LibrarySpectrumID"][i]
        score = input_table["MQScore"][i]
        filename = input_table["SpectrumFile"][i]
        libfilename = input_table["LibraryName"][i]
        scan = input_table["#Scan#"][i]
        TIC_Query = input_table["UnstrictEvelopeScore"][i]
        RT_Query = input_table["p-value"][i]
        SpecCharge = input_table["Charge"][i]
        SpecMZ = input_table["SpecMZ"][i]
        MZErrorPPM = input_table["mzErrorPPM"][i]
        SharedPeaks = input_table["LibSearchSharedPeaks"][i]
        MassDiff = input_table["ParentMassDiff"][i]

        print(spectrum_id)
        gnps_library_spectrum = None
        try:
            gnps_library_spectrum = None
            if spectrum_id in spectrum_id_cache:
                gnps_library_spectrum = spectrum_id_cache[spectrum_id]
            else:
                gnps_library_spectrum = ming_gnps_library.get_library_spectrum(spectrum_id)
                spectrum_id_cache[spectrum_id] = gnps_library_spectrum
        except KeyboardInterrupt:
            raise
        except:
            continue

        output_table["SpectrumID"].append(spectrum_id)
        output_table["Compound_Name"].append(gnps_library_spectrum["annotations"][0]["Compound_Name"])
        output_table["Ion_Source"].append(gnps_library_spectrum["annotations"][0]["Ion_Source"])
        output_table["Instrument"].append(gnps_library_spectrum["annotations"][0]["Instrument"])
        output_table["Compound_Source"].append(gnps_library_spectrum["annotations"][0]["Compound_Source"])
        output_table["PI"].append(gnps_library_spectrum["annotations"][0]["PI"])
        output_table["Data_Collector"].append(gnps_library_spectrum["annotations"][0]["Data_Collector"])
        output_table["Adduct"].append(gnps_library_spectrum["annotations"][0]["Adduct"])
        output_table["Precursor_MZ"].append(gnps_library_spectrum["annotations"][0]["Precursor_MZ"])
        output_table["ExactMass"].append(gnps_library_spectrum["annotations"][0]["ExactMass"])
        output_table["Charge"].append(gnps_library_spectrum["annotations"][0]["Charge"])
        output_table["CAS_Number"].append(gnps_library_spectrum["annotations"][0]["CAS_Number"])
        output_table["Pubmed_ID"].append(gnps_library_spectrum["annotations"][0]["Pubmed_ID"])
        output_table["Smiles"].append(gnps_library_spectrum["annotations"][0]["Smiles"])
        output_table["INCHI"].append(gnps_library_spectrum["annotations"][0]["INCHI"])
        output_table["INCHI_AUX"].append(gnps_library_spectrum["annotations"][0]["INCHI_AUX"])
        output_table["Library_Class"].append(gnps_library_spectrum["annotations"][0]["Library_Class"])
        output_table["IonMode"].append(gnps_library_spectrum["annotations"][0]["Ion_Mode"])

        if gnps_library_spectrum["annotations"][0]["Library_Class"] == "1":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-GOLD")
            output_table["LibraryQualityString"].append("Gold")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "2":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-SILVER")
            output_table["LibraryQualityString"].append("Silver")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "3":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Bronze")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "4":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "5":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "10":
            output_table["UpdateWorkflowName"].append("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_table["LibraryQualityString"].append("Challenge")
        else:
            print("BULLLSHIT", gnps_library_spectrum["annotations"][0]["Library_Class"])

        output_table["#Scan#"].append(scan)
        output_table["SpectrumFile"].append(filename)
        output_table["LibraryName"].append(libfilename)
        output_table["MQScore"].append(score)
        output_table["Organism"].append(gnps_library_spectrum["spectruminfo"]["library_membership"])
        output_table["TIC_Query"].append(TIC_Query)
        output_table["RT_Query"].append(RT_Query)
        output_table["MZErrorPPM"].append(MZErrorPPM)
        output_table["SharedPeaks"].append(SharedPeaks)
        output_table["MassDiff"].append(MassDiff)
        output_table["LibMZ"].append(gnps_library_spectrum["annotations"][0]["Precursor_MZ"])
        output_table["SpecMZ"].append(SpecMZ)
        output_table["SpecCharge"].append(SpecCharge)
        output_table["FileScanUniqueID"].append(input_table["FileScanUniqueID"][i])
        output_table["NumberHits"].append(number_hits_per_query[input_table["FileScanUniqueID"][i]])



        tag_string = ""
        for tag in gnps_library_spectrum["spectrum_tags"]:
            tag_string += tag["tag_desc"].replace("\t", "") + "||"

        if len(tag_string) > 3:
            tag_string = tag_string[:-2]


        output_table["tags"].append(tag_string)

    ming_fileio_library.write_dictionary_table_data(output_table, output_result_filename)




if __name__ == "__main__":
    main()

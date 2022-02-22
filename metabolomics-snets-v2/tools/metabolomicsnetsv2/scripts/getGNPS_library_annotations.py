#!/usr/bin/python

import sys
import os
import pandas as pd
import ming_gnps_library
import requests
from collections import defaultdict
import argparse
import urllib.parse
from tqdm import tqdm

def enrich_output(input_filename, output_filename, topk=None):
    spectrum_id_cache = {}
    molecule_explorer_df = pd.DataFrame(ming_gnps_library.get_molecule_explorer_dataset_data())

    input_results_df = pd.read_csv(input_filename, sep="\t")

    # Here we will try to filter to topk
    if topk is not None:
        try:
            input_results_df["MQScore"] = input_results_df["MQScore"].astype(float)
            input_results_df = input_results_df.sort_values("MQScore", ascending=False)
            input_results_df = input_results_df.groupby('FileScanUniqueID').head(topk).reset_index(drop=True) 
        except:
            pass

    # Counting number of hits per filename
    number_hits_per_query = defaultdict(lambda: 0)
    for result_obj in input_results_df.to_dict(orient="records"):
        number_hits_per_query[result_obj["FileScanUniqueID"]] += 1

    output_list = []
    for result_obj in tqdm(input_results_df.to_dict(orient="records")):
        # Reading exsting data
        spectrum_id = result_obj["LibrarySpectrumID"]
        score = result_obj["MQScore"]
        filename = result_obj["SpectrumFile"]
        libfilename = result_obj["LibraryName"]
        scan = result_obj["#Scan#"]
        TIC_Query = result_obj["UnstrictEvelopeScore"]
        RT_Query = result_obj["p-value"]
        SpecCharge = result_obj["Charge"]
        SpecMZ = result_obj["SpecMZ"]
        MZErrorPPM = result_obj["mzErrorPPM"]
        SharedPeaks = result_obj["LibSearchSharedPeaks"]
        MassDiff = result_obj["ParentMassDiff"]

        print(spectrum_id)
        gnps_library_spectrum = None
        try:
            gnps_library_spectrum = None
            if spectrum_id in spectrum_id_cache:
                gnps_library_spectrum = spectrum_id_cache[spectrum_id]
            else:
                gnps_library_spectrum = ming_gnps_library.get_library_spectrum(spectrum_id)
                spectrum_id_cache[spectrum_id] = gnps_library_spectrum

            #Making sure not an error
            gnps_library_spectrum["annotations"][0]["Compound_Name"]
        except KeyboardInterrupt:
            raise
        except:
            continue

        output_result_dict = {}

        output_result_dict["SpectrumID"] = (spectrum_id)
        output_result_dict["Compound_Name"] = (gnps_library_spectrum["annotations"][0]["Compound_Name"].replace("\t", ""))
        output_result_dict["Ion_Source"] = (gnps_library_spectrum["annotations"][0]["Ion_Source"].replace("\t", ""))
        output_result_dict["Instrument"] = (gnps_library_spectrum["annotations"][0]["Instrument"].replace("\t", ""))
        output_result_dict["Compound_Source"] = (gnps_library_spectrum["annotations"][0]["Compound_Source"].replace("\t", ""))
        output_result_dict["PI"] = (gnps_library_spectrum["annotations"][0]["PI"].replace("\t", ""))
        output_result_dict["Data_Collector"] = (gnps_library_spectrum["annotations"][0]["Data_Collector"].replace("\t", ""))
        output_result_dict["Adduct"] = (gnps_library_spectrum["annotations"][0]["Adduct"].replace("\t", ""))
        output_result_dict["Precursor_MZ"] = (gnps_library_spectrum["annotations"][0]["Precursor_MZ"].replace("\t", ""))
        output_result_dict["ExactMass"] = (gnps_library_spectrum["annotations"][0]["ExactMass"].replace("\t", ""))
        output_result_dict["Charge"] = (gnps_library_spectrum["annotations"][0]["Charge"].replace("\t", ""))
        output_result_dict["CAS_Number"] = (gnps_library_spectrum["annotations"][0]["CAS_Number"].replace("\t", ""))
        output_result_dict["Pubmed_ID"] = (gnps_library_spectrum["annotations"][0]["Pubmed_ID"].replace("\t", ""))
        output_result_dict["Smiles"] = (gnps_library_spectrum["annotations"][0]["Smiles"].replace("\t", ""))
        output_result_dict["INCHI"] = (gnps_library_spectrum["annotations"][0]["INCHI"].replace("\t", ""))
        output_result_dict["INCHI_AUX"] = (gnps_library_spectrum["annotations"][0]["INCHI_AUX"].replace("\t", ""))
        output_result_dict["Library_Class"] = (gnps_library_spectrum["annotations"][0]["Library_Class"].replace("\t", ""))
        output_result_dict["IonMode"] = (gnps_library_spectrum["annotations"][0]["Ion_Mode"].replace("\t", ""))

        if gnps_library_spectrum["annotations"][0]["Library_Class"] == "1":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-GOLD")
            output_result_dict["LibraryQualityString"] = ("Gold")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "2":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-SILVER")
            output_result_dict["LibraryQualityString"] = ("Silver")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "3":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_result_dict["LibraryQualityString"] = ("Bronze")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "4":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_result_dict["LibraryQualityString"] = ("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "5":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_result_dict["LibraryQualityString"] = ("Insilico")
        elif gnps_library_spectrum["annotations"][0]["Library_Class"] == "10":
            output_result_dict["UpdateWorkflowName"] = ("UPDATE-SINGLE-ANNOTATED-BRONZE")
            output_result_dict["LibraryQualityString"] = ("Challenge")
        else:
            print("Invalid Library Class", gnps_library_spectrum["annotations"][0]["Library_Class"])

        output_result_dict["#Scan#"] = (scan)
        output_result_dict["SpectrumFile"] = (filename)
        output_result_dict["LibraryName"] = (libfilename)
        output_result_dict["MQScore"] = (score)
        output_result_dict["Organism"] = (gnps_library_spectrum["spectruminfo"]["library_membership"])
        output_result_dict["TIC_Query"] = (TIC_Query)
        output_result_dict["RT_Query"] = (RT_Query)
        output_result_dict["MZErrorPPM"] = (MZErrorPPM)
        output_result_dict["SharedPeaks"] = (SharedPeaks)
        output_result_dict["MassDiff"] = (MassDiff)
        output_result_dict["LibMZ"] = (gnps_library_spectrum["annotations"][0]["Precursor_MZ"])
        output_result_dict["SpecMZ"] = (SpecMZ)
        output_result_dict["SpecCharge"] = (SpecCharge)
        output_result_dict["FileScanUniqueID"] = (result_obj["FileScanUniqueID"])
        output_result_dict["NumberHits"] = (number_hits_per_query[result_obj["FileScanUniqueID"]])

        if "full_CCMS_path" in result_obj:	
            output_result_dict["full_CCMS_path"] = (result_obj["full_CCMS_path"])

        tag_list = [ (tag["tag_desc"] + "[" + tag["tag_type"] + "]") for tag in gnps_library_spectrum["spectrum_tags"]]
        tag_string = "||".join(tag_list).replace("\t", "")

        output_result_dict["tags"] = (tag_string)

        #Getting molecule explorer information
        compound_name = gnps_library_spectrum["annotations"][0]["Compound_Name"].replace("\t", "")
        compound_filtered_df = molecule_explorer_df[molecule_explorer_df["compound_name"] == compound_name]
        if len(compound_filtered_df) == 1:
            output_result_dict["MoleculeExplorerDatasets"] = (compound_filtered_df.to_dict(orient="records")[0]["number_datasets"])
            output_result_dict["MoleculeExplorerFiles"] = (compound_filtered_df.to_dict(orient="records")[0]["number_files"])
        else:
            output_result_dict["MoleculeExplorerDatasets"] = (0)
            output_result_dict["MoleculeExplorerFiles"] = (0)
        
        # Calculating inchi
        if len(output_result_dict["Smiles"]) > 5 and len(output_result_dict["INCHI"]) < 5:
            try:
                inchi_url = "https://gnps-structure.ucsd.edu/inchi?smiles={}".format(urllib.parse.quote_plus(output_result_dict["Smiles"]), 
                                    urllib.parse.quote_plus(output_result_dict["INCHI"]))
                r = requests.get(inchi_url)
                r.raise_for_status()
                output_result_dict["INCHI"] = r.text
            except:
                output_result_dict["INCHI"] = "N/A"
        
        # Calculating smiles
        if len(output_result_dict["Smiles"]) < 5 and len(output_result_dict["INCHI"]) > 5:
            try:
                smiles_url = "https://gnps-structure.ucsd.edu/smiles?inchi={}".format(urllib.parse.quote_plus(output_result_dict["INCHI"]), 
                                    urllib.parse.quote_plus(output_result_dict["Smiles"]))
                r = requests.get(smiles_url)
                r.raise_for_status()
                output_result_dict["Smiles"] = r.text
            except:
                output_result_dict["Smiles"] = "N/A"

        # Calculating molecular formula
        if len(output_result_dict["Smiles"]) > 5:
            try:
                formula_url = "https://gnps-structure.ucsd.edu/formula?smiles={}".format(output_result_dict["Smiles"])
                r = requests.get(formula_url)
                r.raise_for_status()
                output_result_dict["molecular_formula"] = r.text
            except:
                output_result_dict["molecular_formula"] = "N/A"
        else:
            output_result_dict["molecular_formula"] = "N/A"
         
        # Calculating inchi key
        if len(output_result_dict["Smiles"]) < 5 and len(output_result_dict["INCHI"]) < 5:
            output_result_dict["InChIKey"] = "N/A"
            output_result_dict["InChIKey-Planar"] = "N/A"
        else:
            try:
                inchikey_url = "https://gnps-structure.ucsd.edu/inchikey?smiles={}&inchi={}".format(urllib.parse.quote_plus(output_result_dict["Smiles"]), 
                                    urllib.parse.quote_plus(output_result_dict["INCHI"]))
                r = requests.get(inchikey_url)
                r.raise_for_status()
                output_result_dict["InChIKey"] = r.text
                output_result_dict["InChIKey-Planar"] = r.text.split("-")[0]
            except:
                output_result_dict["InChIKey"] = "N/A"
                output_result_dict["InChIKey-Planar"] = "N/A"

        # Getting Classyfire
        if len(output_result_dict["InChIKey"]) > 5:
            try:
                classyfire_url = "https://gnps-classyfire.ucsd.edu/entities/{}.json".format(output_result_dict["InChIKey"])
                r = requests.get(classyfire_url, timeout=10)
                r.raise_for_status()
                classification_json = r.json()

                output_result_dict["superclass"] = classification_json["superclass"]["name"]
                output_result_dict["class"] = classification_json["class"]["name"]
                output_result_dict["subclass"] = classification_json["subclass"]["name"]
            except:
                output_result_dict["superclass"] = "N/A"
                output_result_dict["class"] = "N/A"
                output_result_dict["subclass"] = "N/A"
        else:
            output_result_dict["superclass"] = "N/A"
            output_result_dict["class"] = "N/A"
            output_result_dict["subclass"] = "N/A"

        # Getting NP Classifier
        if len(output_result_dict["Smiles"]) > 5:
            try:
                npclassifier_url = "https://npclassifier.ucsd.edu/classify?smiles={}".format(output_result_dict["Smiles"])
                r = requests.get(npclassifier_url, timeout=10)
                r.raise_for_status()
                classification_json = r.json()

                output_result_dict["npclassifier_superclass"] = "|".join(classification_json["superclass_results"])
                output_result_dict["npclassifier_class"] = "|".join(classification_json["class_results"])
                output_result_dict["npclassifier_pathway"] = "|".join(classification_json["pathway_results"])
            except:
                output_result_dict["npclassifier_superclass"] = "N/A"
                output_result_dict["npclassifier_class"] = "N/A"
                output_result_dict["npclassifier_pathway"] = "N/A"
        else:
            output_result_dict["npclassifier_superclass"] = "N/A"
            output_result_dict["npclassifier_class"] = "N/A"
            output_result_dict["npclassifier_pathway"] = "N/A"

 
        output_list.append(output_result_dict)

    pd.DataFrame(output_list).to_csv(output_filename, sep="\t", index=False)



def main():
    parser = argparse.ArgumentParser(description='Pulling down GNPS identifcations.')
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    parser.add_argument("--topk", default=None, type=int, help="Top K results per query, default no filter")

    args = parser.parse_args()

    input_result_filename = args.input_filename
    output_result_filename = args.output_filename

    enrich_output(input_result_filename, output_result_filename, topk=args.topk)

if __name__ == "__main__":
    main()

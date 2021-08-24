import sys
import os
import glob
import requests
import pandas as pd
import argparse




parser = argparse.ArgumentParser(description='Invoking new workflow with parameters of given workflow')

parser.add_argument('input_file', help='input_file')
parser.add_argument('output_mgf', help='output_mgf')
parser.add_argument('output_tsv', help='output_tsv')
args = parser.parse_args()

input_filename = args.input_file
split_tup = os.path.splitext(input_filename)

# extract the file name and extension
file_name = split_tup[0]
file_extension = split_tup[1]

if file_extension == '.tsv':
    df = pd.read_csv(input_filename, sep="\t")
elif file_extension == '.csv':
    df = pd.read_csv(input_filename, sep=",")
elif file_extension == '.xlsx':
    df = pd.read_excel(input_filename)

print(df)

all_smiles = []

if "smiles" in df:
    all_smiles = df["smiles"].tolist()

if "SMILES" in df:
    all_smiles = df["SMILES"].tolist()

output_mgf = open(args.output_mgf, "w")

output_results_list = []
scan_count = 1
for smiles in all_smiles:
    url = "http://dorresteinappshub.ucsd.edu:3948/generate/cfmid4"
    #url = "http://mingwangbeta.ucsd.edu:3948/generate/cfmid4"

    r = requests.get(url, params={"smiles": smiles})

    # Calculate precursor m/z from gnps
    adduct_url = "https://gnps-structure.ucsd.edu/adductcalc"
    adduct_r = requests.get(adduct_url, params={"smiles": smiles, "mz": 0})

    if r.status_code == 200 and adduct_r.status_code == 200:
        # We know it only predicts for this Adduct
        adduct_mz = [adduct for adduct in adduct_r.json() if adduct["adduct"] == "M+H"][0]["mz"]

        results = r.json()

        for spectrum in results:
            output_mgf.write("BEGIN IONS\n")
            output_mgf.write("PEPMASS={}\n".format(adduct_mz))
            output_mgf.write("CHARGE=1\n")
            output_mgf.write("SCANS={}\n".format(scan_count))
            for peak in spectrum["peaks"]:
                output_mgf.write("{} {}\n".format(peak[0], peak[1]))
            output_mgf.write("END IONS\n")

            output_dict = {}
            output_dict["filename"] = args.output_mgf
            output_dict["scan"] = scan_count
            output_dict["energy"] = spectrum["energy"]
            output_dict["smiles"] = smiles
            
            scan_count += 1

            output_results_list.append(output_dict)

# Formatting output results
df_results = pd.DataFrame(output_results_list)
df_results.to_csv(args.output_tsv, sep='\t', index=False)




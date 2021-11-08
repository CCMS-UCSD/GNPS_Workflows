import sys
import os
import glob
import requests
from tqdm import tqdm
import pandas as pd

input_filename = sys.argv[1]
output_filename = sys.argv[2]


split_tup = os.path.splitext(input_filename)

# extract the file name and extension
file_name = split_tup[0]
file_extension = split_tup[1]

if file_extension == '.tsv':
    df = pd.read_csv(input_filename, sep="\t")
elif file_extension == '.txt':
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


all_results = []
for smiles in tqdm(all_smiles):
    try:
        url = "https://npclassifier.ucsd.edu/classify"

        r = requests.get(url, params={"smiles": smiles})

        if r.status_code == 200:
            results = r.json()
            results["smiles"] = smiles

            results["class_results"] = ",".join(results["class_results"])
            results["superclass_results"] = ",".join(results["superclass_results"])
            results["pathway_results"] = ",".join(results["pathway_results"])

            all_results.append(results)
    except:
        pass

# Formatting output results
df_results = pd.DataFrame(all_results)
df_results = df_results[["smiles", "class_results", "superclass_results", "pathway_results", "isglycoside"]]
df_results.to_csv(output_filename, sep='\t', index=False)




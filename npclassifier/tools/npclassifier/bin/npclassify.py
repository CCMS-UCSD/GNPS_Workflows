import sys
import os
import glob
import requests
import pandas as pd

input_filename = sys.argv[1]
output_filename = sys.argv[2]


split_tup = os.path.splitext(input_filename)

# extract the file name and extension
file_name = split_tup[0]
file_extension = split_tup[1]

if file_extension == '.tsv' or file_extension == '.csv':
    df = pd.read_csv(input_filename, sep=None)
elif file_extension == '.xlsx':
    df = pd.read_excel(input_filename)

all_records = df.to_dict(orient='records')

all_smiles = []

if "smiles" in df:
    all_smiles = df["smiles"].tolist()

if "SMILES" in df:
    all_smiles = df["SMILES"].tolist()


all_results = []
for smiles in all_smiles:
    url = "https://npclassifier.ucsd.edu/classify"

    r = requests.get(url, params={"smiles": smiles})

    if r.status_code == 200:
        results = r.json()
        print(results)
        all_results.append(results)

# Formatting output results
df_results = pd.DataFrame(all_results)
df_results.to_csv(output_filename, sep='\t', index=False)




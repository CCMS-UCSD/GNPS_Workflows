import pandas as pd
import os
import sys
import requests
import shutil

"""TODO: Handle no metadata file input"""

input_metadata_filename = sys.argv[1]
input_quantification_table = sys.argv[2]
output_folder = sys.argv[3]

output_metadata_filename = os.path.join(output_folder, "qiime2_metadata.tsv")
output_manifest_filename = os.path.join(output_folder, "qiime2_manifest.tsv")

df_quantification = pd.read_csv(input_quantification_table, sep=",")

if len(input_metadata_filename) > 2:
    df_metadata = pd.read_csv(input_metadata_filename, sep="\t")
    if "sample_name" in df_metadata:
        manifest_df = df_metadata["sample_name", "filename"]
    else:
        manifest_df = pd.DataFrame()
        manifest_df["sample_name"] = df_metadata["filename"]
        manifest_df["filepath"] = df_metadata["filename"]
else:
    df_metadata = pd.DataFrame([{"filename": "placeholder"}])


"""Checking if the set of filenames are fully covered, if not then we'll provide a place holder"""
all_quantification_filenames = [key.split(" ")[0] for key in df_quantification.keys() if "Peak area" in key]

manifest_filenames = list(manifest_df["filepath"])

manifest_object_list = manifest_df.to_dict(orient="records")
for quantification_filename in all_quantification_filenames:
    if not quantification_filename in manifest_filenames:
        print(quantification_filename, "not found")
        manifest_object = {}
        manifest_object["filepath"] = quantification_filename
        manifest_object["sample_name"] = quantification_filename
        manifest_object_list.append(manifest_object)

pd.DataFrame(manifest_object_list).to_csv(output_manifest_filename, index=False, sep=",")

"""Reformatting the metadata filename"""
if "sample_name" in df_metadata:
    new_output_metadata = df_metadata
else:
    new_output_metadata = df_metadata
    new_output_metadata["sample_name"] = df_metadata["filename"]

output_columns = list(new_output_metadata.keys())
output_columns.remove("sample_name")
output_columns.insert(0, "sample_name")
new_output_metadata.to_csv(output_metadata_filename, index=False, sep="\t", columns=output_columns)

"""Calling remote server to do the calculation"""
SERVER_BASE = "http://dorresteinappshub.ucsd.edu:5024"
files = {'manifest': open(output_manifest_filename, 'r'), 'metadata': open(output_metadata_filename, 'r'), 'quantification': open(input_quantification_table, 'r')}
r_post = requests.post(SERVER_BASE + "/process", files=files)
response_dict = r_post.json()

with open(os.path.join(output_folder, "qiime2_table.qza"), 'wb') as f:
    r = requests.get(SERVER_BASE + response_dict["table_qza"], stream=True)
    r.raw.decode_content = True
    shutil.copyfileobj(r.raw, f)

with open(os.path.join(output_folder, "qiime2_emperor.qzv"), 'wb') as f:
    r = requests.get(SERVER_BASE + response_dict["emperor_qzv"], stream=True)
    r.raw.decode_content = True
    shutil.copyfileobj(r.raw, f)

import requests
import sys
import pandas as pd
import os
import shutil
import glob

input_mmvec_folder = sys.argv[1]
input_taxonomy_file = sys.argv[2]
input_molecules_file = sys.argv[3]
output_filename = sys.argv[4]

conditional_probabilities = os.path.join(input_mmvec_folder, "conditional.qza")

unzip_cmd = "unzip -o {}".format(conditional_probabilities)
print(unzip_cmd)
os.system(unzip_cmd)

conditionals_tsv = glob.glob("**/conditionals.tsv", recursive=True)
if len(conditionals_tsv) != 1:
    print("Can't find conditional probabilities")
    exit(1)

#Reading input
conditionals_df = pd.read_csv(conditionals_tsv[0], sep="\t")
taxa_metadata_df = pd.read_csv(input_taxonomy_file, sep="\t")
molecules_metadata_df = pd.read_csv(input_molecules_file, sep="\t")


all_molecules = list(conditionals_df.keys())[1:]

output_records = []
all_records = conditionals_df.to_dict(orient="records")

for record in all_records:
    taxa_sequence = record["featureid"]
    for molecule in all_molecules:
        output_record = {}
        conditional_value = record[molecule]
        output_record["taxa_sequence"] = taxa_sequence
        output_record["conditional_value"] = conditional_value
        output_record["molecule_identifier"] = molecule

        output_records.append(output_record)

# Trying to figure out the metadata headers
taxa_featureid_header = "featureid"
if "Feature ID" in taxa_metadata_df:
    taxa_featureid_header = "Feature ID"

metabolomics_feature_header = "featureid"
if "sampleid" in molecules_metadata_df:
    metabolomics_feature_header = "sampleid"
if "#Scan#" in molecules_metadata_df:
    metabolomics_feature_header = "#Scan#"
if "Feature Information" in molecules_metadata_df:
    metabolomics_feature_header = "Feature Information"

# Merging the files
records_df = pd.DataFrame(output_records)
records_df = records_df.merge(taxa_metadata_df, how="left", left_on="taxa_sequence", right_on=taxa_featureid_header)
records_df = records_df.merge(molecules_metadata_df, how="left", left_on="molecule_identifier", right_on=metabolomics_feature_header)

records_df.to_csv(output_filename, sep="\t", index=False)











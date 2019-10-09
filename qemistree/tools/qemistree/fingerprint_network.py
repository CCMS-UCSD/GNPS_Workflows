#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse
import glob

def similarity(fingerprint_dict1, fingerprint_dict2):
    dict1_fingerprints = set([key for key in fingerprint_dict1 if fingerprint_dict1[key] > 0.5])
    dict2_fingerprints = set([key for key in fingerprint_dict2 if fingerprint_dict2[key] > 0.5])

    intersection = dict1_fingerprints & dict2_fingerprints
    union = dict1_fingerprints | dict2_fingerprints
    
    jaccard_index = float(len(intersection))/float(len(union))
    
    return jaccard_index

def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("fingerprint_summary_folder")
    parser.add_argument("output_folder")

    args = parser.parse_args()
    input_filename = os.path.join(args.fingerprint_summary_folder, "summary_fingerprints.tsv")
    df = pd.read_csv(input_filename, sep="\t")

    all_records = df.to_dict(orient="records")
    all_records_reformatted = []

    for record in all_records:
        new_dict = {}
        new_dict["feature_id"] = record["feature_id"]
        record.pop("feature_id")
        new_dict["fingerprint_scores"] = record
        all_records_reformatted.append(new_dict)

    output_list = []
    for record1 in all_records_reformatted:
        for record2 in all_records_reformatted:
            if int(record1["feature_id"]) <= int(record2["feature_id"]):
                continue

            output_dict = {}
            output_dict["SCAN1"] = record1["feature_id"]
            output_dict["SCAN2"] = record2["feature_id"]

            sim = similarity(record1["fingerprint_scores"], record2["fingerprint_scores"])

            output_dict["sim"] = sim

            output_list.append(output_dict)

    pd.DataFrame(output_list).to_csv(os.path.join(args.output_folder, "pairs.tsv"), sep="\t", index=False)


    
            










if __name__ == "__main__":
    main()

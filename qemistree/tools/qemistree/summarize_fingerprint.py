#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse
import glob

def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("results_folder")
    parser.add_argument("summary_folder")

    args = parser.parse_args()

    input_csi_qza = os.path.join(args.results_folder, "fingerprints.qza")
    cmd = "unzip -o {}".format(input_csi_qza)
    print(cmd)
    os.system(cmd)

    #Looking for summary filename
    search_filenames = glob.glob("**/csi-output/summary_csi_fingerid.csv", recursive=True)

    if len(search_filenames) == 1:
        summary_filename = search_filenames[0]
        df = pd.read_csv(summary_filename, sep="\t")

        df.to_csv(os.path.join(args.summary_folder, "summary_csi.tsv"), sep="\t", index=False)


    #Loading fingerprint mapping
    fingerprint_mapping_filenames = glob.glob("**/data/csi-output/fingerprints.csv", recursive=True)
    fingerprint_mapping = {}
    if len(fingerprint_mapping_filenames) == 1:
        df = pd.read_csv(fingerprint_mapping_filenames[0], sep="\t")
        for fingerprint_record in df.to_dict(orient="records"):
            index = fingerprint_record["relativeIndex"]
            description = fingerprint_record["description"]
            fingerprint_mapping[index] = description

    #Loading all the actual fingerprints
    output_fingerprint_summary_list = []
    all_features_folder = glob.glob("**/csi-output/*_features_*", recursive=True)
    for feature_folder in all_features_folder:
        fingerprint_filenames = glob.glob(os.path.join(feature_folder, "fingerprints/*.fpt"))
        if len(fingerprint_filenames) != 1:
            continue

        feature_id = os.path.basename(feature_folder).split("_")[0]

        feature_dict = {}
        feature_dict["feature_id"] = feature_id

        i = 0
        for line in open(fingerprint_filenames[0]):
            fingerprint_value = float(line.rstrip())
            fingerprint_name = fingerprint_mapping[i]
            feature_dict["FINGERPRINT_{}".format(fingerprint_name)] = fingerprint_value
            i += 1

        output_fingerprint_summary_list.append(feature_dict)

    pd.DataFrame(output_fingerprint_summary_list).to_csv(os.path.join(args.summary_folder, "summary_fingerprints.tsv"), sep="\t", index=False)
        





if __name__ == "__main__":
    main()

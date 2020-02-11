import pandas as pd
import os
import sys
import requests
import shutil
import argparse
import glob

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_metadata_filename', help='input_metadata_filename')
    parser.add_argument('input_quantification_table', help='input_quantification_table')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument("conda_activate_bin")
    parser.add_argument("conda_environment")
    args = parser.parse_args()

    output_metadata_filename = os.path.join(args.output_folder, "qiime2_metadata.tsv")
    output_manifest_filename = os.path.join(args.output_folder, "qiime2_manifest.tsv")

    df_quantification = pd.read_csv(args.input_quantification_table, sep=",")

    """Reading Metadata Filename and filling in empty entries"""
    if len(args.input_metadata_filename) < 2:
        df_metadata = pd.DataFrame([{"filename": "placeholder"}])
    elif os.path.isfile(args.input_metadata_filename):
        df_metadata = pd.read_csv(args.input_metadata_filename, sep="\t")
    else:
        #It is a directory
        metadata_files = glob.glob(os.path.join(args.input_metadata_filename, "*"))
        if len(metadata_files) > 1:
            print("Enter only a single metadata file")
            exit(1)
        elif len(metadata_files) == 0:
            df_metadata = pd.DataFrame([{"filename": "placeholder"}])
        else:
            df_metadata = pd.read_csv(metadata_files[0], sep="\t")

    if not "sample_name" in df_metadata:
        df_metadata["sample_name"] = df_metadata["filename"]

    """Checking if the set of filenames are fully covered, if not then we'll provide a place holder"""
    all_quantification_filenames = [key.replace("Peak area", "").rstrip() for key in df_quantification.keys() if "Peak area" in key]
    metadata_filenames = []
    try:
        metadata_filenames = list(df_metadata["filename"])
    except:
        metadata_filenames

    metadata_object_list = df_metadata.to_dict(orient="records")
    for quantification_filename in all_quantification_filenames:
        if not quantification_filename in metadata_filenames:
            print(quantification_filename, "not found")
            metadata_object = {}
            metadata_object["filename"] = quantification_filename
            metadata_object["sample_name"] = quantification_filename
            metadata_object_list.append(metadata_object)

    """Adding in missing filenames into the metadata"""
    new_output_metadata = pd.DataFrame(metadata_object_list)

    #Removing protected headers
    new_output_metadata = new_output_metadata.drop(columns=["feature", "#SampleID"], errors="ignore")

    output_columns = list(new_output_metadata.keys())
    output_columns.remove("sample_name")
    output_columns.insert(0, "sample_name")

    new_output_metadata.to_csv(output_metadata_filename, index=False, sep="\t", columns=output_columns, na_rep="NaN")

    """Outputting Manifest Filename"""
    manifest_df = pd.DataFrame()
    manifest_df["sample_name"] = new_output_metadata["sample_name"]
    manifest_df["filepath"] = new_output_metadata["filename"]
    manifest_df.to_csv(output_manifest_filename, index=False, sep=",")

    #Running Qiime2
    local_qza_table = os.path.join(args.output_folder, "qiime2_table.qza")
    local_qza_relative_table = os.path.join(args.output_folder, "qiime2_relative_table.qza")
    local_qza_distance = os.path.join(args.output_folder, "qiime2_distance.qza")
    local_qza_pcoa = os.path.join(args.output_folder, "qiime2_pcoa.qza")
    local_qzv_emperor = os.path.join(args.output_folder, "qiime2_emperor.qzv")
    local_qza_biplot = os.path.join(args.output_folder, "qiime2_biplot.qza")
    local_qzv_biplot_emperor = os.path.join(args.output_folder, "qiime2_biplot_emperor.qzv")


    all_cmd = []
    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime metabolomics import-mzmine2 \
        --p-manifest {} \
        --p-quantificationtable {} \
        --o-feature-table {}".format(args.conda_activate_bin, args.conda_environment, output_manifest_filename, args.input_quantification_table, local_qza_table))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime diversity beta \
        --i-table {} \
        --p-metric cosine \
        --o-distance-matrix {}".format(args.conda_activate_bin, args.conda_environment, local_qza_table, local_qza_distance))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime diversity pcoa \
        --i-distance-matrix {} \
        --o-pcoa {}".format(args.conda_activate_bin, args.conda_environment, local_qza_distance, local_qza_pcoa))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime emperor plot \
        --i-pcoa {} \
        --m-metadata-file {} \
        --o-visualization {} \
        --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, local_qza_pcoa, output_metadata_filename, local_qzv_emperor))

    #Biplotting
    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime feature-table relative-frequency \
        --i-table {} \
        --o-relative-frequency-table  {}".format(args.conda_activate_bin, args.conda_environment, local_qza_table, local_qza_relative_table))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime diversity pcoa-biplot \
        --i-pcoa {} \
        --i-features {} \
        --o-biplot {}".format(args.conda_activate_bin, args.conda_environment, local_qza_pcoa, local_qza_relative_table, local_qza_biplot))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime emperor biplot \
        --i-biplot {} \
        --m-sample-metadata-file {} \
        --p-number-of-features 10 \
        --o-visualization {} \
        --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, local_qza_biplot, output_metadata_filename, local_qzv_biplot_emperor))


    for cmd in all_cmd:
        os.system(cmd)



if __name__ == "__main__":
    main()

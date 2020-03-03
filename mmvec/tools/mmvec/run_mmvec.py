import requests
import sys
import pandas as pd
import os
import shutil
import glob
import argparse

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_metabolomics_features', help='input_metabolomics_features')
    parser.add_argument('input_metabolomics_feature_metadata', help='input_metabolomics_feature_metadata')
    parser.add_argument('import_microbial_features', help='import_microbial_features')
    parser.add_argument('import_microbial_feature_metadata', help='import_microbial_feature_metadata')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument("conda_activate_bin")
    parser.add_argument("conda_environment")
    parser.add_argument("--epochs", default="100")
    parser.add_argument("--latentdim", default="5")
    args = parser.parse_args()

    #Checking if header names are appropriate, if not, then lets correct them. Need to fix and test: https://github.com/biocore/mmvec/tree/master/examples/cf
    temp_reformatted_metadata_filename = os.path.join(args.output_folder, "reformatted_metabolomics_identifications.tsv")
    metabolomics_metadata_df = pd.read_csv(args.input_metabolomics_feature_metadata, sep="\t")

    if "Feature Information" in metabolomics_metadata_df: # It has Feature Information, so lets rename
        headers = list(metabolomics_metadata_df.keys())
        metabolomics_metadata_df["featureid"] = metabolomics_metadata_df["Feature Information"]
        headers = ["featureid"] + headers
        try:
            headers.remove('id')
        except:
            pass
        metabolomics_metadata_df.to_csv(temp_reformatted_metadata_filename, columns=headers, sep="\t", index=False)
    #Checking for scan numbers in the header
    elif "#Scan#" in metabolomics_metadata_df: # This is from Library Idenfications from GNPS
        headers = list(metabolomics_metadata_df.keys())
        metabolomics_metadata_df["featureid"] = metabolomics_metadata_df["#Scan#"]
        headers = ["featureid"] + headers
        try:
            headers.remove('id')
        except:
            pass
        print(headers)
        metabolomics_metadata_df.to_csv(temp_reformatted_metadata_filename, columns=headers, sep="\t", index=False)
    else: # Others
        print("Copying")
        shutil.copyfile(args.input_metabolomics_feature_metadata, temp_reformatted_metadata_filename)

    # Commands to Execute
    all_cmd = []

    #Copying input files into the correct location
    mmvec_output_directory = args.output_folder
    metabolite_qza = os.path.join(mmvec_output_directory, "metabolite_features.qza")
    microbiome_qza = os.path.join(mmvec_output_directory, "microbe_features.qza")

    #Making sure the input files are qza
    if os.path.splitext(args.input_metabolomics_features)[1] == ".qza":
        shutil.copyfile(args.input_metabolomics_features, metabolite_qza)
    elif os.path.splitext(args.input_metabolomics_features)[1] == ".biom":
        #Do Conversion
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime tools import \
            --input-path {} \
            --output-path {} \
            --type FeatureTable[Frequency]".format(args.conda_activate_bin, args.conda_environment, args.input_metabolomics_features, metabolite_qza))
    if os.path.splitext(args.import_microbial_features)[1] == ".qza":
        shutil.copyfile(args.import_microbial_features, microbiome_qza)
    elif os.path.splitext(args.import_microbial_features)[1] == ".biom":
        #Do Conversion
        all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
            qiime tools import \
            --input-path {} \
            --output-path {} \
            --type FeatureTable[Frequency]".format(args.conda_activate_bin, args.conda_environment, args.import_microbial_features, microbiome_qza))

    #Running Qiime2 mmvec
    LATENT_DIM = int(args.latentdim)
    LEARNING_RATE = 0.001
    EPOCHS = int(args.epochs)

    local_metabolite_metadata_filename = temp_reformatted_metadata_filename
    local_microbial_metadata_filename = args.import_microbial_feature_metadata

    conditional = os.path.join(mmvec_output_directory, "conditional.qza")
    conditional_biplot = os.path.join(mmvec_output_directory, "conditional_biplot.qza")
    output_emperor = os.path.join(mmvec_output_directory, "emperor.qzv")

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime mmvec paired-omics \
        --p-latent-dim {} \
        --p-learning-rate {} \
        --p-epochs {} \
        --i-microbes {} \
        --i-metabolites {} \
        --o-conditionals {} \
        --o-conditional-biplot {}".format(args.conda_activate_bin, args.conda_environment, \
        LATENT_DIM, LEARNING_RATE, EPOCHS, \
        metabolite_qza, microbiome_qza, conditional, conditional_biplot))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime emperor biplot \
        --i-biplot {} \
        --m-sample-metadata-file {} \
        --m-feature-metadata-file {} \
        --o-visualization {} \
        --p-ignore-missing-samples".format(args.conda_activate_bin, args.conda_environment, conditional_biplot, local_metabolite_metadata_filename, local_microbial_metadata_filename, output_emperor))

    for cmd in all_cmd:
        print(cmd)
        os.system(cmd)

if __name__ == "__main__":
    main()
